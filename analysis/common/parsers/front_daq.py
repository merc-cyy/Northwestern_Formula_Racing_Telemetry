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

        # ——— build the struct format string ———
        fmt = (
            "<"
            + "3i"  # hour, minute, second (ints)
            + "4f"  # 4 wheel speeds
            + "B"  # driveState (uint8)
            + "7f"  # HVVoltage, LVVoltage, batteryTemp,
            +
            # maxCellTemp, minCellTemp, maxCellVoltage, minCellVoltage
            f"{BMS_FAULT_COUNT}B"  # BMS fault flags (bytes)
            + f"{NUM_VOLT_CELLS}f"  # cell voltages
            + f"{NUM_TEMP_CELLS}f"  # cell temperatures
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

        # ——— allocate CarDB (zeroed by default) ———
        db = CarDB(n_records)

        with open(filename, "rb") as f:
            for i in range(n_records):
                chunk = f.read(record_size)
                vals = struct.unpack(fmt, chunk)
                idx = 0
                rec = db._db[i]

                # — time —
                h, m, s = vals[idx : idx + 3]
                idx += 3
                rec["time"]["hour"] = h
                rec["time"]["minute"] = m
                rec["time"]["second"] = s
                # time_since_startup & millis remain 0

                # — wheel speeds —
                for w in range(4):
                    rec["corners"][w]["wheel_speed"] = vals[idx]
                    idx += 1

                # — drive state —
                ds = vals[idx]
                idx += 1
                rec["ecu"]["drive_state"] = ds
                rec["bms"]["bms_state"] = ds

                # — HV/LV/batteryTemp/max/min temps & voltages —
                (hv, lv, bat_t, max_t, min_t, max_v, min_v) = vals[idx : idx + 7]
                idx += 7
                rec["bms"]["soe_bat_voltage"] = hv
                rec["pdm"]["bat_voltage"] = lv
                rec["bms"]["soe_bat_temp"] = bat_t

                # — BMS faults & ECU implausibilities —
                raw_faults = vals[idx : idx + BMS_FAULT_COUNT]
                idx += BMS_FAULT_COUNT
                bools = [bool(x) for x in raw_faults]
                rec["bms"]["faults"] = bools
                rec["ecu"]["implausibilities"] = bools[:5]

                # — cell voltages —
                volts = vals[idx : idx + NUM_VOLT_CELLS]
                idx += NUM_VOLT_CELLS
                rec["bms"]["cell_voltages"] = np.array(volts, dtype=np.float32)

                # — cell temperatures —
                temps = vals[idx : idx + NUM_TEMP_CELLS]
                idx += NUM_TEMP_CELLS
                rec["bms"]["cell_temps"] = np.array(temps, dtype=np.float32)

                # all other fields (suspension, IMU, GPS, PDM amps, inverter, etc.)
                # remain at their default zero values

        return db
