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
        # Unpack everything in one shot
        vals = struct.unpack_from(LINE_FMT, raw)
        i = 0

        # ── SECTION 1: Timestamp ─────────────────────────────────────────────────────
        dest["time"]["time_since_startup"] = vals[i]
        i += 1
        # (We don’t store hour/min/sec/millis from the struct here.)

        # ── SECTION 2: BMS faults (8 bools) ─────────────────────────────────────────
        dest["bms"]["fault_summary"] = int(vals[i])
        i += 1
        dest["bms"]["undervoltage_fault"] = bool(vals[i])
        i += 1
        dest["bms"]["overvoltage_fault"] = bool(vals[i])
        i += 1
        dest["bms"]["undertemperature_fault"] = bool(vals[i])
        i += 1
        dest["bms"]["overtemperature_fault"] = bool(vals[i])
        i += 1
        dest["bms"]["overcurrent_fault"] = bool(vals[i])
        i += 1
        dest["bms"]["external_kill_fault"] = bool(vals[i])
        i += 1
        dest["bms"]["open_wire_fault"] = bool(vals[i])
        i += 1

        # ── SECTION 3: ECU implausibility flags (5 bools) ────────────────────────────
        dest["ecu"]["implausibilities"] = vals[i : i + ECU_FAULT_COUNT]
        i += ECU_FAULT_COUNT

        # ── SECTION 5: BMS “summary” floats (25 floats: hvVoltage…pumpAmps) ──────────
        (
            hvV,
            lvV,
            batT,
            maxCT,
            minCT,
            maxCV,
            minCV,
            maxD,
            maxR,
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
            genA,
            fanA,
            pumpA,
        ) = vals[i : i + 25]
        i += 25

        # We only store the ones your CarDB cares about:
        dest["bms"]["battery_voltage"] = hvV
        dest["bms"]["battery_temp"] = batT
        dest["bms"]["max_cell_voltage"] = maxCV
        dest["bms"]["min_cell_voltage"] = minCV
        dest["bms"]["max_cell_temp"] = maxCT
        dest["bms"]["min_cell_temp"] = minCT
        dest["bms"]["soc"] = soc
        dest["bms"]["max_discharge_current"] = maxD
        dest["bms"]["max_regen_current"] = maxR
        
        dest["pdm"]["bat_voltage"] = lvV


        # ── SECTION 6: Corner data (4 corners × (speed, displacement, strain)) ────
        for idx, (wsp, wdp, pr) in enumerate(
            zip((ws0, ws1, ws2, ws3), (wd0, wd1, wd2, wd3), (ps0, ps1, ps2, ps3))
        ):
            dest["corners"][idx]["wheel_speed"] = wsp
            dest["corners"][idx]["wheel_displacement"] = wdp
            dest["corners"][idx]["pr_strain"] = pr

        # ── SECTION 7: PDM amps ──────────────────────────────────────────────────────
        dest["pdm"]["gen_amps"] = genA
        dest["pdm"]["fan_amps"] = fanA
        dest["pdm"]["pump_amps"] = pumpA

        # ── SECTION 8: uint16/int16 heart of inverter & apps/brakes (11 values) ───
        (
            rawFaults,  # uint16
            rpm,
            motI,
            dcV,
            dcI,  # int16
            fBP,
            rBP,
            apps1,
            apps2,  # int16
            igbtT,
            motT,  # uint16
        ) = vals[i : i + 11]
        i += 11
        dest["inverter"]["rpm"] = rpm
        dest["inverter"]["motor_current"] = motI
        dest["inverter"]["dc_voltage"] = dcV
        dest["inverter"]["dc_current"] = dcI
        dest["inverter"]["igbt_temp"] = igbtT
        dest["inverter"]["motor_temp"] = motT


        dest["ecu"]["apps1_throttle"] = apps1
        dest["ecu"]["apps2_throttle"] = apps2
        dest["ecu"]["front_brake_pressure"] = fBP
        dest["ecu"]["rear_brake_pressure"] = rBP        

        # ── SECTION 9: ECU state bytes (5×uint8) ────────────────────────────────────
        (driveSt, bmsSt, imdSt, invSt, bmsCmd) = vals[i : i + 5]
        i += 5
        dest["ecu"]["drive_state"] = int(driveSt)
        dest["bms"]["bms_state"] = int(bmsSt)
        dest["bms"]["imd_state"] = int(imdSt)
        dest["ecu"]["bms_command"] = int(bmsCmd)

        # ── SECTION 10: 4×bool: brakePressed, lvVoltageWarning, pdmEfuses ──────────
        dest["ecu"]["brake_pressed"] = bool(vals[i])
        i += 1
        dest["pdm"]["bat_voltage_warning"] = bool(vals[i])
        i += 1
        dest["pdm"]["gen_efuse_triggered"] = bool(vals[i])
        i += 1
        dest["pdm"]["pump_efuse_triggered"] = bool(vals[i])
        i += 1


        # ── SECTION 12: 4×uint32 + 2×int32 (Ah/Wh drawn/charged, set currents) ────
        (ahDrawn, ahChgd, whDrawn, whChgd, setC, setCB) = vals[i : i + 6]
        i += 6
        dest["inverter"]["ah_drawn"] = ahDrawn
        dest["inverter"]["ah_charged"] = ahChgd
        dest["inverter"]["wh_drawn"] = whDrawn
        dest["inverter"]["wh_charged"] = whChgd
        dest["ecu"]["set_current"] = setC
        dest["ecu"]["set_current_brake"] = setCB

        # ── SECTION 13: pump/fan duty, aero, LUT id, resets, temp‐limit, torque ───
        dest["ecu"]["pump_duty_cycle"] = vals[i]
        i += 1
        dest["ecu"]["fan_duty_cycle"] = vals[i]
        i += 1
        dest["ecu"]["active_aero_state"] = bool(vals[i])
        i += 1
        dest["ecu"]["active_aero_position"] = vals[i]
        i += 1
        dest["ecu"]["accel_lut_id_response"] = int(vals[i])
        i += 1
        dest["pdm"]["reset_gen_efuse"] = bool(vals[i])
        i += 1
        dest["pdm"]["reset_ac_efuse"] = bool(vals[i])
        i += 1
        dest["ecu"]["igbt_temp_limiting"] = bool(vals[i])
        i += 1
        dest["ecu"]["battery_temp_limiting"] = bool(vals[i])
        i += 1
        dest["ecu"]["motor_temp_limiting"] = bool(vals[i])
        i += 1
        dest["ecu"]["torque_status"] = int(vals[i])
        i += 1


        # ── SECTION 15: 32 temperature readings (flo0…fri7) ─────────────────────────
        temps_32 = vals[i : i + 32]
        i += 32
        # it goes fl_temperature (0-7), fr_temperature (0-7),
        # bl_temperature (0-7), br_temperature (0-7)
        dest["corners"][0]["wheel_temperature"][:] = temps_32[0:8]  # fl
        dest["corners"][1]["wheel_temperature"][:] = temps_32[8:16]  # fr
        dest["corners"][2]["wheel_temperature"][:] = temps_32[16:24]  # bl
        dest["corners"][3]["wheel_temperature"][:] = temps_32[24:32]  # br

        # ── SECTION 16: 12 floats: fl_*, fr_*, bl_*, br_* (3 per corner) ────────────
        corners_12 = vals[i : i + 12]
        i += 12
        # assign in order: fl_speed, fl_disp, fl_load, fr_…, bl_…, br_…
        keys = [
            ("corners", 0, "wheel_speed"),
            ("corners", 0, "wheel_displacement"),
            ("corners", 0, "pr_strain"),
            ("corners", 1, "wheel_speed"),
            ("corners", 1, "wheel_displacement"),
            ("corners", 1, "pr_strain"),
            ("corners", 2, "wheel_speed"),
            ("corners", 2, "wheel_displacement"),
            ("corners", 2, "pr_strain"),
            ("corners", 3, "wheel_speed"),
            ("corners", 3, "wheel_displacement"),
            ("corners", 3, "pr_strain"),
        ]
        for (blk, idx, key), v in zip(keys, corners_12):
            dest[blk][idx][key] = v

        # ── SECTION 17: File & LUT metadata (4×uint8 + …) ──────────────────────────
        i += 4


        # # ── SECTION 18: 30 × (int16 x_n, float y_n) ───────────────────────────────
        # # (we don’t store this in CarDB, so we skip it)
        i += 30 * 2 # int16, two pads, float

        # ── SECTION 19: 3 floats: acceleration & angular speed ─────────────────────────────────────
        dest["dynamics"]["imu"]["accel"] = vals[i : i + 3]
        i += 3

        # ── SECTION 20: 3 floats: angular speed ────────────────────────────────────
        dest["dynamics"]["imu"]["vel"] = vals[i : i + 3]
        i += 3

        # ── SECTION 21: 8 floats: air_speed_0…7 ────────────────────────────────────
        dest["dynamics"]["air_speed"] = vals[i : i + 8]
        i += 8

        # ── SECTION 22: 2 floats: flow rates ───────────────────────────────────────
        dest["dynamics"]["coolant_flow"] = vals[i]
        i += 2

        # ── SECTION 23: 2 floats : coolant temperatures ─────────────────────────────
        dest["dynamics"]["coolant_temps"] = vals[i : i + 2]
        i += 2

        # ── SECTION 23: unix timestamp & lat/lon ───────────────────────────────────
        dest["time"]["unix_time"] = vals[i]
        i += 1
        dest["dynamics"]["gps_location"][:] = vals[i : i + 2]
        i += 2

        # skip the statuses
        i += 22

        # ── SECTION 26: steering_angle & then the 80+140 BMS arrays ────────────────
        dest["dynamics"]["steering_angle"] = vals[i]
        i += 1

        # store cell temperatures and voltages
        dest["bms"]["cell_temps"][:] = vals[i : i + NUM_TEMP_CELLS]
        i += NUM_TEMP_CELLS
        dest["bms"]["cell_voltages"][:] = vals[i : i + NUM_VOLT_CELLS]
        i += NUM_VOLT_CELLS   

        # we stored the cell temps and voltages again...
        # skip it again
        i += NUM_TEMP_CELLS + NUM_VOLT_CELLS
    

        # ── FINAL CHECK ──────────────────────────────────────────────────────────────
        if i != len(vals):
            raise ValueError(f"Decoded {i} of {len(vals)} values")

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
        print(f"Parsing {n} records from {filename} ({len(data)} bytes)")
        db = CarDB(n)
        mv = memoryview(data)
        for idx in range(n):
            start = idx * LINE_SIZE
            self._decode_record(mv[start : start + LINE_SIZE], db._db[idx])
        return db
