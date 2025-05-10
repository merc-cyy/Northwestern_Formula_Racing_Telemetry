"""
FrontDAQ   ·   binary log → CarDB
Firmware: teensy/src/logger.cpp  (9-byte 'NFR25' preamble + 1 004-byte records)
Parser:   FrontDAQ v1
"""

from __future__ import annotations
import os
import struct
import numpy as np

from analysis.common.parser_registry import (
    ParserVersion,
    parser_class,
    BaseParser,
)
from analysis.common.car_db import CarDB


# ──────────────────────────────────────────────────────────────────────────
#                       Constants – mirror the firmware
# ──────────────────────────────────────────────────────────────────────────
NUM_TEMP_CELLS = 80
NUM_VOLT_CELLS = 140
BMS_FAULT_COUNT = 8  # summary, underV, overV, underT, overT, overI, extKill, openWire
ECU_FAULT_COUNT = 5  # implausibility flags we care about
PREAMBLE_LEN = 9  # 'NFR25' + 3 bytes + 1 byte record-size


# ─────────────────────────── DriveBusData layout ─────────────────────────
# 13 bools  + 3 pad           = 16         (compiler padded to 4-byte boundary)
# 22 floats                    88
# 1 uint16  + 4 int16          10
# 4 uint8  + 1 bool + 1 pad     6          (final pad → 120 total)
DRIVE_FMT = (
    "8?"  # BMS faults
    "5?"  # ECU faults
    "3x"  # pad → align floats
    "22f"  # hv, lv, temps, wheel speeds, etc.
    "H"  # bmsFaultsRaw
    "4h"  # motor rpm / currents / voltages
    "4B"  # driveState, bmsState, imdState, inverterStatus
    "?"  # lvVoltageWarning
    "x"  # final pad
)
assert struct.calcsize("<" + DRIVE_FMT) == 120, "DriveBusData size mis-match"

# One whole log line:  millis + Drive + 80T + 140V  = 1 004 B
LINE_FMT = "<I" + DRIVE_FMT + f"{NUM_TEMP_CELLS + NUM_VOLT_CELLS}f"
LINE_SIZE = struct.calcsize(LINE_FMT)
assert LINE_SIZE == 1004, LINE_SIZE


# Parser Class
@parser_class(ParserVersion("NFR25", 0, 0, 1))
class FrontDAQParser(BaseParser):
    """
    Parse *.bin files written by the FrontDAQ, version 1 (5/10/25) logger and return
    a fully-typed CarDB.
    """

    @staticmethod
    def _decode_record(raw: memoryview, dest: np.void) -> None:
        """Decode one 1 004-byte record directly into the CarDB slot."""
        vals = struct.unpack_from(LINE_FMT, raw)
        i = 0

        #  time (millis since power-on)
        dest["time"]["time_since_startup"] = vals[i]
        i += 1

        # BMS + ECU faults (13 bools)
        dest["bms"]["faults"][:] = vals[i : i + BMS_FAULT_COUNT]
        dest["ecu"]["implausibilities"][:] = vals[
            i + BMS_FAULT_COUNT : i + BMS_FAULT_COUNT + ECU_FAULT_COUNT
        ]
        i += BMS_FAULT_COUNT + ECU_FAULT_COUNT + 0  # pad skipped by struct

        # 22 floats
        hv, lv, batT, maxT, minT, maxV, minV, maxDis, maxReg, soc, *rest = vals[
            i : i + 22
        ]
        i += 22

        dest["bms"]["soe_bat_voltage"] = hv
        dest["pdm"]["bat_voltage"] = lv
        dest["bms"]["soe_bat_temp"] = batT
        dest["bms"]["soe_max_discharge_current"] = maxDis
        dest["bms"]["soe_max_regen_current"] = maxReg
        dest["bms"]["bms_state"] = 0  # set below

        # wheelSpeeds[4] + wheelDisp[4] + prStrain[4] are in *rest*
        ws, wd, ps = rest[0:4], rest[4:8], rest[8:12]
        for w in range(4):
            dest["corners"][w]["wheel_speed"] = ws[w]
            dest["corners"][w]["wheel_displacement"] = wd[w]
            dest["corners"][w]["pr_strain"] = ps[w]

        #  uint16 + 4×int16 (motor info)
        _bmsFaultsRaw, rpm, motI, dcV, dcI = vals[i : i + 5]
        i += 5
        dest["inverter"]["rpm"] = rpm
        dest["inverter"]["motor_current"] = motI
        dest["inverter"]["dc_voltage"] = dcV
        dest["inverter"]["dc_current"] = dcI

        # 4×uint8 + 1 bool
        driveState, bmsState, _imd, _invStat = vals[i : i + 4]
        i += 4
        dest["ecu"]["drive_state"] = driveState
        dest["bms"]["bms_state"] = bmsState
        dest["pdm"]["bat_voltage_warning"] = vals[i]
        i += 1
        # final pad consumed by struct

        # cell temps & voltages
        j = i + NUM_TEMP_CELLS
        dest["bms"]["cell_temps"][:] = vals[i:j]
        i = j
        j = i + NUM_VOLT_CELLS
        dest["bms"]["cell_voltages"][:] = vals[i:j]

    @staticmethod
    def parse(filename: str) -> CarDB:
        with open(filename, "rb") as fh:
            pre = fh.read(PREAMBLE_LEN)
            if len(pre) < PREAMBLE_LEN or not pre.startswith(b"NFR25001"):
                print("Missing 'NFR25001' preamble")
                return
            if pre[-1] != LINE_SIZE:
                print(f"Firmware line-size {pre[-1]} ≠ parser {LINE_SIZE}")
                return
            blob = fh.read()

        if len(blob) % LINE_SIZE:
            raise ValueError("File length is not a multiple of record size")

        n = len(blob) // LINE_SIZE
        db = CarDB(n)

        mv = memoryview(blob)
        for rec_idx in range(n):
            start = rec_idx * LINE_SIZE
            FrontDAQParser._decode_record(
                mv[start : start + LINE_SIZE], db._db[rec_idx]
            )

        return db
