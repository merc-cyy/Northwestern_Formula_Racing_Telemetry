from __future__ import annotations
import struct
import numpy as np

from analysis.common.parser_registry import ParserVersion, parser_class, BaseParser
from analysis.common.car_db import CarDB, car_snapshot_dtype

from analysis.common.parsers.fmt_front_daq_002 import fmt

# ─── constants ────────────────────────────────────────────────────────────────
NUM_TEMP_CELLS = 80
NUM_VOLT_CELLS = 140
BMS_FAULT_COUNT = 8  # summary, underV, overV, underT, overT, overI, extKill, openWire
ECU_FAULT_COUNT = 5  # implausibility flags

PREAMBLE_MAGIC = b"NFR25"
PREAMBLE_LEN = len(PREAMBLE_MAGIC)  # =5
VERSION_BYTES = 3  # major, minor, patch
SKIP_BYTES = 1  # record-size (mod 256)

# Build DRIVE_FMT by concatenating pieces, each with a one-line comment
DRIVE_FMT = fmt.removeprefix("<")

assert (
    struct.calcsize("<" + DRIVE_FMT) == 1600
), f"DriveBusData size mismatch, expected 1600, got {struct.calcsize('<' + DRIVE_FMT)}"

# ─── now append your 80+140 floats from DataBusData ────────────────────────────────
DATA_FMT = f"{NUM_TEMP_CELLS}f{NUM_VOLT_CELLS}f"

# ─── full record: 4B timestamp + DRIVE_FMT + DATA_FMT ─────────────────────────────
LINE_FMT = "<I" + DRIVE_FMT + DATA_FMT
LINE_SIZE = struct.calcsize(LINE_FMT)


@parser_class(ParserVersion("NFR25", 0, 0, 2))
class FullDAQParser(BaseParser):
    def _decode_record(self, raw: memoryview, dest: np.void) -> None:
        vals = struct.unpack_from(LINE_FMT, raw)
        i = 0

        # ── 1) timestamp ─────────────────────────────────────────────────────────
        dest["time"]["time_since_startup"] = vals[i]
        i += 1

        # ── 2) bmsFaults + ecu implausibilities ────────────────────────────────
        dest["bms"]["fault_summary":] = vals[i : i + BMS_FAULT_COUNT]  # all 8
        i += BMS_FAULT_COUNT
        dest["ecu"]["implausibilities"][:] = vals[i : i + ECU_FAULT_COUNT]
        i += ECU_FAULT_COUNT

        # ── 3) 25 floats: hvVoltage … pumpAmps ────────────────────────────────
        (
            hv,
            lv,
            batT,
            maxCellT,
            minCellT,
            maxCellV,
            minCellV,
            maxDis,
            maxReg,
            soc,
            ws0,
            ws1,
            ws2,
            ws3,
            wd0,
            wd1,
            wd2,
            wd3,
            ps0,
            ps1,
            ps2,
            ps3,
            genAmps,
            fanAmps,
            pumpAmps,
        ) = vals[i : i + 25]
        i += 25

        # map into CarDB
        dest["bms"]["max_discharge_current"] = maxDis
        dest["bms"]["max_regen_current"] = maxReg
        dest["bms"]["battery_temp"] = batT
        dest["bms"]["battery_voltage"] = lv
        dest["bms"]["soc"] = soc
        dest["bms"]["max_cell_temp"] = maxCellT
        dest["bms"]["min_cell_temp"] = minCellT
        dest["bms"]["max_cell_voltage"] = maxCellV
        dest["bms"]["min_cell_voltage"] = minCellV

        # ── 4) corners from wheelSpeeds, wheelDisplacement, prStrain ─────────
        for idx, (wsp, wdp, pr) in enumerate(
            zip((ws0, ws1, ws2, ws3), (wd0, wd1, wd2, wd3), (ps0, ps1, ps2, ps3))
        ):
            dest["corners"][idx]["wheel_speed"] = wsp
            dest["corners"][idx]["wheel_displacement"] = wdp
            dest["corners"][idx]["pr_strain"] = pr

        # ── 5) PDM amps ─────────────────────────────────────────────────────────
        dest["pdm"]["gen_amps"] = genAmps
        dest["pdm"]["fan_amps"] = fanAmps
        dest["pdm"]["pump_amps"] = pumpAmps

        # ── 6) next 11 values: bmsFaultsRaw + motor…temps ─────────────────────
        #   (_, rpm, motI, dcV, dcI, fBP, rBP, app1, app2, igbtT, motT)
        _, rpm, motI, dcV, dcI, *_tail = vals[i : i + 11]
        i += 11
        dest["inverter"]["rpm"] = rpm
        dest["inverter"]["motor_current"] = motI
        dest["inverter"]["dc_voltage"] = dcV
        dest["inverter"]["dc_current"] = dcI
        # note: we ignore frontBrake... and apps here; CarDB doesn't store them

        # ── 7) 5×uint8: driveState, bmsState, imdState, invStatus, bmsCommand ─
        driveState, bmsState, imdState, _invSt, _bCmd = vals[i : i + 5]
        i += 5
        dest["ecu"]["drive_state"] = driveState
        dest["bms"]["bms_state"] = bmsState
        dest["bms"]["imd_state"] = imdState

        # ── 8) 2×bool: brakePressed, lvVoltageWarning ────────────────────────
        brake, lvWarn = vals[i : i + 2]
        i += 2
        dest["ecu"]["brake_pressed"] = bool(brake)
        dest["pdm"]["bat_voltage_warning"] = bool(lvWarn)

        # ── 9) 2×bool: pdm efuse triggers ─────────────────────────────────────
        genEf, acEf = vals[i : i + 2]
        i += 2
        dest["pdm"]["gen_efuse_triggered"] = bool(genEf)
        dest["pdm"]["fan_efuse_triggered"] = False  # not in DriveBusData
        dest["pdm"]["pump_efuse_triggered"] = False  # ditto

        # ── 10) 4×uint32 & 2×int32: Ah/Wh drawn/charged + set currents ───────
        ahDrawn, ahChg, whDrawn, whChg, setC, setCB = vals[i : i + 6]
        i += 6
        dest["inverter"]["ah_drawn"] = ahDrawn
        dest["inverter"]["ah_charged"] = ahChg
        dest["inverter"]["wh_drawn"] = whDrawn
        dest["inverter"]["wh_charged"] = whChg
        dest["ecu"]["set_current"] = setC
        dest["ecu"]["set_current_brake"] = setCB

        # ── 11) pump/fan duty, aero, LUT resp, reset efuse, temp-limit, torque ─
        pumpDuty, fanDuty = vals[i : i + 2]
        i += 2
        aeroSt, aeroPos = vals[i : i + 2]
        i += 2
        lutID = vals[i]
        i += 1
        rGen, rAC = vals[i : i + 2]
        i += 2
        il, bl, ml = vals[i : i + 3]
        i += 3
        torque = vals[i]
        i += 1

        dest["ecu"]["pump_duty_cycle"] = pumpDuty
        dest["ecu"]["fan_duty_cycle"] = fanDuty
        dest["ecu"]["active_aero_state"] = bool(aeroSt)
        dest["ecu"]["active_aero_position"] = aeroPos
        dest["ecu"]["accel_lut_id_response"] = int(lutID)
        dest["pdm"]["reset_gen_efuse"] = bool(rGen)
        dest["pdm"]["reset_ac_efuse"] = bool(rAC)
        dest["ecu"]["igbt_temp_limiting"] = bool(il)
        dest["ecu"]["battery_temp_limiting"] = bool(bl)
        dest["ecu"]["motor_temp_limiting"] = bool(ml)
        dest["ecu"]["torque_status"] = int(torque)

        # ── 12) skip 32 + 12 floats + 4 bytes + 60 values + 3+3+8+2+2 values + 1+2+2+3+3+4+3+3+4+1 values ─
        skip = (
            32
            + 12
            + 4
            + 60
            + (3 + 3 + 8 + 2 + 2)
            + (1 + 2 + 2 + 3 + 3 + 4 + 3 + 3 + 4 + 1)
        )
        i += skip

        # ── 13) finally: BMS cell temps & voltages ─────────────────────────────
        temps = vals[i : i + NUM_TEMP_CELLS]
        i += NUM_TEMP_CELLS
        volts = vals[i : i + NUM_VOLT_CELLS]
        dest["bms"]["cell_temps"][:] = temps
        dest["bms"]["cell_voltages"][:] = volts

        # skip the duplicated 80+140 floats at the end
        # (they are already in the CarDB schema, so we don't need to decode them again)
        i += 80 + 140

    def parse(self, filename: str) -> CarDB:
        # print(f"DriveBusData format: {DRIVE_FMT}, size {LINE_SIZE} bytes")
        with open(filename, "rb") as fh:
            header = fh.read(PREAMBLE_LEN + VERSION_BYTES + SKIP_BYTES)
            if not header.startswith(PREAMBLE_MAGIC):
                raise ValueError(f"{filename}: missing 'NFR25' header")
            data = fh.read()

        if len(data) % LINE_SIZE:
            raise ValueError(
                f"{filename}: {len(data)} bytes not a multiple of {LINE_SIZE}, remainder {len(data) % LINE_SIZE},"
            )

        n = len(data) // LINE_SIZE
        db = CarDB(n)
        mv = memoryview(data)
        for idx in range(n):
            start = idx * LINE_SIZE
            self._decode_record(mv[start : start + LINE_SIZE], db._db[idx])
        return db
