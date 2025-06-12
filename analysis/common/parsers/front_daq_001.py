from __future__ import annotations
import struct
import numpy as np

from analysis.common.parser_registry import ParserVersion, parser_class, BaseParser
from analysis.common.car_db        import CarDB


NUM_TEMP_CELLS  = 80
NUM_VOLT_CELLS  = 140
BMS_FAULT_COUNT = 8   # summary, underV, overV, underT, overT, overI, extKill, openWire
ECU_FAULT_COUNT = 5   # implausibility flags
PREAMBLE_MAGIC  = b"NFR25"
PREAMBLE_LEN    = len(PREAMBLE_MAGIC)  # =5
VERSION_BYTES   = 3   # major, minor, patch
SKIP_BYTES      = 1   # record-size (mod 256)

# DriveBusData struct (total 148 B) 
DRIVE_FMT = (
    "8?"    # bmsFaults[8]
    "5?"    # ecuFaults[5]
    "3x"    # pad → align to 4
    "25f"   # hvVoltage…pumpAmps (10 + 4 + 4 + 4 + 3)
    "H"     # bmsFaultsRaw
    "8h"    # motorRPM, motorCurrent, motorDCVoltage, motorDCCurrent,
            # frontBrakePressure, rearBrakePressure, apps1, apps2
    "2H"    # inverterIGBTTemp, inverterMotorTemp
    "5B"    # driveState, bmsState, imdState, inverterStatus, bmsCommand
    "2?"    # brakePressed, lvVoltageWarning
    "3x"    # final pad → round up to 4-byte boundary
)
assert struct.calcsize("<" + DRIVE_FMT) == 148, "DriveBusData size mismatch"

# ─── one full record = 4 B millis + 148 B drive + (80+140) × 4 B data = 1 032 B
LINE_FMT  = "<I" + DRIVE_FMT + f"{NUM_TEMP_CELLS}f{NUM_VOLT_CELLS}f"
LINE_SIZE = struct.calcsize(LINE_FMT)
assert LINE_SIZE == 1032, LINE_SIZE


@parser_class(ParserVersion("NFR25", 0, 0, 1))
class FrontDAQParser(BaseParser):
    def _decode_record(self, raw: memoryview, dest: np.void) -> None:
        vals = struct.unpack_from(LINE_FMT, raw)
        i = 0

        # ── timestamp ────────────────────────────────
        dest["time"]["time_since_startup"] = vals[i];  i += 1

        # ── BMS + ECU faults ─────────────────────────
        dest["bms"]["faults"][:]           = vals[i : i + BMS_FAULT_COUNT]
        dest["ecu"]["implausibilities"][:] = vals[
            i + BMS_FAULT_COUNT : i + BMS_FAULT_COUNT + ECU_FAULT_COUNT
        ]
        i += BMS_FAULT_COUNT + ECU_FAULT_COUNT

        # ── 25 floats: hv…pumpAmps ──────────────────
        (
            hv, lv, batT,
            maxT, minT, maxV, minV,
            maxDis, maxReg, _bmsSOC,   # SOC not in CarDB schema → ignore
            ws0, ws1, ws2, ws3,
            wd0, wd1, wd2, wd3,
            ps0, ps1, ps2, ps3,
            genAmps, fanAmps, pumpAmps
        ) = vals[i : i + 25]
        i += 25

        # map into CarDB
        dest["bms"]["soe_bat_voltage"]        = hv
        dest["pdm"]["bat_voltage"]            = lv
        dest["bms"]["soe_bat_temp"]           = batT
        dest["bms"]["soe_max_discharge_current"] = maxDis
        dest["bms"]["soe_max_regen_current"]     = maxReg

        # corners
        dest["corners"][0]["wheel_speed"]        = ws0
        dest["corners"][1]["wheel_speed"]        = ws1
        dest["corners"][2]["wheel_speed"]        = ws2
        dest["corners"][3]["wheel_speed"]        = ws3
        dest["corners"][0]["wheel_displacement"] = wd0
        dest["corners"][1]["wheel_displacement"] = wd1
        dest["corners"][2]["wheel_displacement"] = wd2
        dest["corners"][3]["wheel_displacement"] = wd3
        dest["corners"][0]["pr_strain"]          = ps0
        dest["corners"][1]["pr_strain"]          = ps1
        dest["corners"][2]["pr_strain"]          = ps2
        dest["corners"][3]["pr_strain"]          = ps3

        # PDM amps
        dest["pdm"]["gen_amps"]  = genAmps
        dest["pdm"]["fan_amps"]  = fanAmps
        dest["pdm"]["pump_amps"] = pumpAmps

        # ── 1×uint16 + 8×int16 + 2×uint16 ────────────
        (
            _bRaw,
            rpm, motI, dcV, dcI,
            fBP, rBP, app1, app2,
            igbtT, motT
        ) = vals[i : i + 11]
        i += 11
        dest["inverter"]["rpm"]           = rpm
        dest["inverter"]["motor_current"] = motI
        dest["inverter"]["dc_voltage"]    = dcV
        dest["inverter"]["dc_current"]    = dcI
        # (frontBrakePressure, rearBrakePressure, apps, temps are
        # not in the CarDB schema, so we skip them)

        # ── 5×uint8 → drive/bms states + bmsCommand ────
        driveState, bmsState, _imd, _invSt, _bCmd = vals[i : i + 5]
        i += 5
        dest["ecu"]["drive_state"] = driveState
        dest["bms"]["bms_state"]   = bmsState

        # ── 2×bool: brakePressed, lvVoltageWarning ─────
        brake, lvWarn = vals[i : i + 2]
        i += 2
        dest["ecu"]["brake_pressed"]        = brake
        dest["pdm"]["bat_voltage_warning"]  = lvWarn

        # ── DataBusData: temps then volts ──────────────
        temps = vals[i : i + NUM_TEMP_CELLS];    i += NUM_TEMP_CELLS
        volts = vals[i : i + NUM_VOLT_CELLS]
        dest["bms"]["cell_temps"][:]     = temps
        dest["bms"]["cell_voltages"][:]  = volts


    def parse(self, filename: str) -> CarDB:
        with open(filename, "rb") as fh:
            # 1) magic
            header = fh.read(PREAMBLE_LEN + VERSION_BYTES + SKIP_BYTES)
            if not header.startswith(PREAMBLE_MAGIC):
                raise ValueError("Missing 'NFR25' header")
            # 2) (major,minor,patch) = header[5:8], skip record-size = header[8]
            data = fh.read()

        if len(data) % LINE_SIZE:
            raise ValueError(
                f"{filename}: {len(data)} bytes not a multiple of {LINE_SIZE}"
            )

        n = len(data) // LINE_SIZE
        db = CarDB(n)
        mv = memoryview(data)
        for idx in range(n):
            start = idx * LINE_SIZE
            self._decode_record(mv[start : start + LINE_SIZE], db._db[idx])

        return db
