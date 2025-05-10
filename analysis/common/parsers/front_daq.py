import os
import struct#used to interpret binary files
import numpy as np

from analysis.common.parser_registry import (
    ParserVersion,# can return the specfiic parser given a version and given a file, can find the rigth version, and parse it
    parser_class,#the actual implementation of parsing a file
    BaseParser,#base parser
)
from analysis.common.car_db import CarDB#the blueprint for the data


@parser_class(ParserVersion("FrontDAQ", 0, 0, 0))
class FrontDAQParser(BaseParser):
    @staticmethod
    def parse(filename: str) -> CarDB:#takes in the binary file we want to read and returns it as a CarDB
        # ——— match your C++ #defines ———
        NUM_TEMP_CELLS = 80#info on 80 temp cells
        NUM_VOLT_CELLS = 140#info on 140 voltage cells
        BMS_FAULT_COUNT = 8#8 bms records

        # ——— build the struct format string ———
        fmt = (
            "<" #little endian binary format
            + "3i"  # hour, minute, second (ints) first3 ints are hour, min, sec
            + "4f"  # 4 wheel speeds #next 4 floats are speeds of all 4 wheels
            + "B"  # driveState (uint8)
            + "7f"  # HVVoltage, LVVoltage, batteryTemp,
            +
            # maxCellTemp, minCellTemp, maxCellVoltage, minCellVoltage
            f"{BMS_FAULT_COUNT}B"  # BMS fault flags (bytes) -> 8 of them
            + f"{NUM_VOLT_CELLS}f"  # cell voltages
            + f"{NUM_TEMP_CELLS}f"  # cell temperatures
        )
        record_size = struct.calcsize(fmt)#size of each data record in bytes

        # ——— sanity-check file size ———
        total_bytes = os.path.getsize(filename)
        if total_bytes % record_size != 0:
            print(
                f"'{filename}' is {total_bytes} bytes, "
                f"not a multiple of {record_size}"
            )
            return
        n_records = total_bytes // record_size

        # ——— allocate CarDB (zeroed by default) ———
        db = CarDB(n_records)#init CarDB with the number of entries

        with open(filename, "rb") as f:#open file and read it as binary
            for i in range(n_records):#for each record,
                chunk = f.read(record_size)#read the whole chunk/record
                vals = struct.unpack(fmt, chunk)#vals is a tuple containing the extracted values 
                idx = 0
                rec = db._db[i]#rec is the space for this specific record since DB can hold many records

                # — time —
                h, m, s = vals[idx : idx + 3]
                idx += 3
                rec["time"]["hour"] = h
                rec["time"]["minute"] = m
                rec["time"]["second"] = s#save the hr, min and sec in rec's fields
                # time_since_startup & millis remain 0

                # — wheel speeds —
                for w in range(4):
                    rec["corners"][w]["wheel_speed"] = vals[idx]
                    idx += 1 #save the wheel speeds 

                # — drive state —
                ds = vals[idx]
                idx += 1
                rec["ecu"]["drive_state"] = ds
                rec["bms"]["bms_state"] = ds#set drive state to both ecu and bms

                # — HV/LV/batteryTemp/max/min temps & voltages —
                (hv, lv, bat_t, max_t, min_t, max_v, min_v) = vals[idx : idx + 7]
                idx += 7
                rec["bms"]["soe_bat_voltage"] = hv#set high voltage
                rec["pdm"]["bat_voltage"] = lv #set low voltage
                rec["bms"]["soe_bat_temp"] = bat_t #set battery temp

                # — BMS faults & ECU implausibilities —
                raw_faults = vals[idx : idx + BMS_FAULT_COUNT]#all bms data
                idx += BMS_FAULT_COUNT
                bools = [bool(x) for x in raw_faults]#for all bms data convert to t or f
                rec["bms"]["faults"] = bools
                rec["ecu"]["implausibilities"] = bools[:5]

                # — cell voltages —
                volts = vals[idx : idx + NUM_VOLT_CELLS]
                idx += NUM_VOLT_CELLS
                rec["bms"]["cell_voltages"] = np.array(volts, dtype=np.float32)#array of cell voltages

                # — cell temperatures —
                temps = vals[idx : idx + NUM_TEMP_CELLS]
                idx += NUM_TEMP_CELLS
                rec["bms"]["cell_temps"] = np.array(temps, dtype=np.float32)#bms cell temperatures

                # all other fields (suspension, IMU, GPS, PDM amps, inverter, etc.)
                # remain at their default zero values

        return db

