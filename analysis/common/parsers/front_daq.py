import os
import struct
import numpy as np

from analysis.common.parser_registry import (
    ParserVersion,
    parser_class,
    BaseParser,
)
from analysis.common.car_db import CarDB


@parser_class(ParserVersion("FrontDAQ", 0))
class FrontDAQParser(BaseParser):
    @staticmethod
    def parse(filename: str) -> CarDB:
        # ——— match your C++ #defines ———
        NUM_TEMP_CELLS = 80
        NUM_VOLT_CELLS = 140
        BMS_FAULT_COUNT = 8

        # ——— build a struct fmt string ———
        # 3 ints, 4 floats, 1 byte, 7 floats,
        # BMS_FAULT_COUNT bytes,
        # NUM_VOLT_CELLS floats,
        # NUM_TEMP_CELLS floats
        fmt = "<" + "".join(
            [
                "3i",  # hour, minute, second
                "4f",  # wheelSpeeds
                "B",  # driveState
                "7f",  # HV, LV, batTemp, max/min temps & voltages
                f"{BMS_FAULT_COUNT}B",  # bmsFaults
                f"{NUM_VOLT_CELLS}f",  # cellVoltages
                f"{NUM_TEMP_CELLS}f",  # cellTemperatures
            ]
        )
        record_size = struct.calcsize(fmt)

        # ——— sanity-check file size ———
        total_bytes = os.path.getsize(filename)
        if total_bytes % record_size != 0:
            raise ValueError(
                f"'{filename}' is {total_bytes} bytes, "
                f"not a multiple of {record_size}"
            )
        n_records = total_bytes // record_size

        # ——— allocate a zeroed CarDB ———
        db = CarDB(n_records)

        with open(filename, "rb") as f:
            for i in range(n_records):
                chunk = f.read(record_size)
                vals = struct.unpack(fmt, chunk)
                idx = 0

                # --- time ---
                h, m, s = vals[idx : idx + 3]
                idx += 3
                db._db[i]["time"]["hour"] = h
                db._db[i]["time"]["minute"] = m
                db._db[i]["time"]["second"] = s
                # time_since_startup & millis stay 0

                # --- wheel speeds ---
                for w in range(4):
                    db._db[i]["corners"][w]["wheel_speed"] = vals[idx]
                    idx += 1

                # --- driveState → ECU.drive_state & BMS.bms_state ---
                ds = vals[idx]
                idx += 1
                db._db[i]["ecu"]["drive_state"] = ds
                db._db[i]["bms"]["bms_state"] = ds

                # --- HV/LV/batTemp/max/min temps & voltages ---
                hv, lv, bat_t, max_t, min_t, max_v, min_v = vals[idx : idx + 7]
                idx += 7
                db._db[i]["bms"]["soe_bat_voltage"] = hv
                db._db[i]["pdm"]["bat_voltage"] = lv
                db._db[i]["bms"]["soe_bat_temp"] = bat_t

                # --- BMS faults & ECU implausibilities ---
                faults = vals[idx : idx + BMS_FAULT_COUNT]
                idx += BMS_FAULT_COUNT
                bools = [bool(x) for x in faults]
                db._db[i]["bms"]["faults"] = bools
                db._db[i]["ecu"]["implausibilities"] = bools

                # --- cell voltages ---
                volts = vals[idx : idx + NUM_VOLT_CELLS]
                idx += NUM_VOLT_CELLS
                db._db[i]["bms"]["cell_voltages"] = np.array(volts, dtype=np.float32)

                # --- cell temperatures ---
                temps = vals[idx : idx + NUM_TEMP_CELLS]
                idx += NUM_TEMP_CELLS
                db._db[i]["bms"]["cell_temps"] = np.array(temps, dtype=np.float32)

                # everything else (suspension, IMU, GPS, PDM amps, inverter, etc.)
                # remains at the zero default in CarDB

        return db
