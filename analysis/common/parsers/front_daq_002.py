from __future__ import annotations
import struct
import numpy as np

from analysis.common.parser_registry import ParserVersion, parser_class, BaseParser
from analysis.common.car_db import CarDB, car_snapshot_dtype

# ─── constants ────────────────────────────────────────────────────────────────
NUM_TEMP_CELLS = 80
NUM_VOLT_CELLS = 140
BMS_FAULT_COUNT = 8   # bmsFaults[]
ECU_FAULT_COUNT = 5   # ecuFaults[]

# ─── drive-bus struct (DriveBusData) ───────────────────────────────────────────
# (you must fill in the exact field runs & paddings here to match your C++ sizeof)
DRIVE_FMT = (
    f"{BMS_FAULT_COUNT}?{ECU_FAULT_COUNT}?"  # bmsFaults[], ecuFaults[]
    "3x"            # pad to 4
    "25f"           # hvVoltage…pumpAmps
    "H"             # bmsFaultsRaw
    "8h"            # motorRPM…apps2
    "2H"            # inverterIGBTTemp, inverterMotorTemp
    "5B"            # driveState…bmsCommand
    "2?"            # brakePressed, lvVoltageWarning
    "2?"            # pdmGenEfuseTriggered, pdmACEfuseTriggered
    "x"             # pad to 4
    "2I2I2i"        # inverterAhDrawn,AhCharged ; WhDrawn,WhCharged ; EcuSetCurrent,SetCurrentBrake
    "Bh?hBh??B"     # pump_duty_cycle, fan_duty_cycle, active_aero_state, active_aero_position,
                    # accel_lut_id_response, reset_efuses, temp_limiting, torque_status
    "32f"           # flo_…, fli_…, fro_…, fri_…, blo_…, bli_…, bro_…, bri_… (8 wheels × 4 temps)
    "12f"           # fl_speed/fl_disp/fl_load, fr_…, bl_…, br_…
    "4B"            # file_status, num_lut_pairs, interp_type, lut_id
    "60h60f"        # 30×(int16,float) LUT pairs
    "3f3f8f2f2f"    # acceleration(3), gyro(3), air_speed[8], flow[2], temp[2]
    "I2f2B3B3B4Bf"  # time_since_1970, lon/lat, wireless/logger, enable/response flags, statuses, steering_angle
)

# ─── extra data arrays (DataBusData) ───────────────────────────────────────────
DATA_FMT = f"{NUM_TEMP_CELLS}f{NUM_VOLT_CELLS}f"

# ─── full record = uint32 + DRIVE_FMT + DATA_FMT ──────────────────────────────
LINE_FMT  = "<I" + DRIVE_FMT + DATA_FMT
LINE_SIZE = struct.calcsize(LINE_FMT)
assert LINE_SIZE == car_snapshot_dtype.itemsize, (
    f"Record size ({LINE_SIZE}) ≠ numpy dtype size ({car_snapshot_dtype.itemsize})"
)

@parser_class(ParserVersion("NFR25", 0, 0, 2))
class CarSnapshotParser(BaseParser):
    def parse(self, filename: str) -> CarDB:
        # 1) read & validate header
        header_len = len(b"NFR25") + 3 + 1
        with open(filename, "rb") as fh:
            header = fh.read(header_len)
            if not header.startswith(b"NFR25"):
                raise ValueError(f"{filename}: missing 'NFR25' header")
            data = fh.read()

        # 2) make sure we have whole records
        n_bytes = len(data)
        if n_bytes % LINE_SIZE:
            raise ValueError(
                f"{filename}: {n_bytes} bytes is not a multiple of {LINE_SIZE}"
            )
        n = n_bytes // LINE_SIZE

        # 3) bulk-decode into a NumPy array of your car_snapshot_dtype
        arr = np.frombuffer(data, dtype=car_snapshot_dtype)
        if arr.shape[0] != n:
            raise RuntimeError("Record count mismatch after decoding")

        # 4) wrap in CarDB
        db = CarDB(n)
        db._db[:] = arr
        return db
