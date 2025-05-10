##converts a csv to db

from analysis.common.car_db import CarDB
from analysis.common.car_db import car_snapshot_dtype

import os
import csv
import numpy as np


# ——— Constants ———
NUM_TEMP_CELLS = 80#info on 80 temp cells
NUM_VOLT_CELLS = 140#info on 140 voltage cells
BMS_FAULT_COUNT = 8#8 bms records
GPS_COORDS = 2  # e.g. lat, lon



def getlen_csv(filepath: str):

    # length = 0
    # with open(filepath, 'r') as f:
    #     read = csv.reader(f)
    #     read = next(read)#skip the header

    #     for _ in read:
    #         length += 1

    # return length

    length = 0
    try:
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip the header, None avoids StopIteration error
            for row in reader:
                if row:  # check if the row is not empty
                    length += 1
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return 0
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return 0
    return length


def csv_to_db(csvfilepath: str):
    if not os.path.exists(csvfilepath):
        print("Pass in a valid csv file")
        return
    
    #init a CarDb
    entries = getlen_csv(csvfilepath)#get the number of snapshots
    if not entries:
        print("Error getting length of csv")
        return
    #print(f"LENGTH OF CSV:{entries}")
    db = CarDB(entries)#init DB iwth the number of snapshots

    #read in the csv line by line
    with open(csvfilepath, 'r') as csvfile:#open csv file and read it in
        reader = csv.reader(csvfile)
        header = next(reader)  # Read the header row
        #print(f"Header: {header}")#the columns

        for i, line in enumerate(reader):#for each snapshot, each line is a snapshot 
            if i < entries:
                rec = db._db[i]#store our snapshot; find a way to save all the 'snapshots' into the final cardb
                vals = [v.strip() for v in line] # Clean up line values

                #line has the values we need
                #map the fields in each line to the Cardb
                #- time -
                try:
                    if 'hour' in header:
                        rec["time"]["hour"] = np.uint8(vals[header.index('hour')]) if vals[header.index('hour')] else np.uint8(0)
                    if 'minute' in header:
                        rec["time"]["minute"] = np.uint8(vals[header.index('minute')]) if vals[header.index('minute')] else np.uint8(0)
                    if 'second' in header:
                        rec["time"]["second"] = np.uint8(vals[header.index('second')]) if vals[header.index('second')] else np.uint8(0)
                    if 'time_since_startup' in header:
                        rec["time"]["time_since_startup"] = np.uint32(vals[header.index('time_since_startup')]) if vals[header.index('time_since_startup')] else 0
                    if 'millis' in header:
                        rec["time"]["millis"] = np.uint16(vals[header.index('millis')]) if vals[header.index('millis')] else np.uint16(0)

                    # — wheel speeds —
                    
                    for w in range(4):
                        col = f"corners{w}_wheel_speed"
                        if col in header and (vals[header.index(col)]):#if that col exists and the value is not 0
                            rec["corners"][w]["wheel_speed"] = np.float32(vals[header.index(col)])
                        else:
                            rec["corners"][w]["wheel_speed"] = np.float32(0)
                        

                    # — drive state —
                    if 'bms_state' in header and (vals[header.index('bms_state')]):#if drive state is there
                        ds = np.int32(vals[header.index('bms_state')])
                    else:
                        ds = np.int32(0)
                    rec["ecu"]["drive_state"] = ds
                    rec["bms"]["bms_state"] = ds#set drive state to both ecu and bms

                    # --- HV/LV/Battery Temp/Max/Min Temps & Voltages ---
                    if 'bms_soe_bat_voltage' in header:
                        rec["bms"]["soe_bat_voltage"] = np.float32(vals[header.index('bms_soe_bat_voltage')]) if vals[header.index('bms_soe_bat_voltage')] else np.float32(0)
                    if 'pdm_bat_voltage' in header:
                        rec["pdm"]["bat_voltage"] = np.float32(vals[header.index('pdm_bat_voltage')]) if vals[header.index('pdm_bat_voltage')] else np.float32(0)
                    if 'bms_soe_bat_temp' in header:
                        rec["bms"]["soe_bat_temp"] = np.float32(vals[header.index('bms_soe_bat_temp')]) if vals[header.index('bms_soe_bat_temp')] else np.float32(0)

                # --- BMS Faults & ECU Implausibilities ---
                    bms_fault_cols = [f'bms_fault_{i+1}' for i in range(BMS_FAULT_COUNT)]
                    bms_faults = []
                    for col in bms_fault_cols:
                        if col in header:
                            bms_faults.append(bool(int(vals[header.index(col)])) if vals[header.index(col)] else False)
                    if len(bms_faults) == BMS_FAULT_COUNT:
                        rec["bms"]["faults"] = np.array(bms_faults, dtype=bool)
                        rec["ecu"]["implausibilities"] = np.array(bms_faults[:5], dtype=bool)

                    # --- Cell Voltages ---
                    cell_voltage_cols = [f'bms_cell_voltages_{i+1}' for i in range(NUM_VOLT_CELLS)]
                    cell_voltages = []
                    for col in cell_voltage_cols:
                        if col in header and vals[header.index(col)]:
                            cell_voltages.append(np.float32(vals[header.index(col)])) 
                        else:
                            cell_voltages.append(np.float32(0))
                    if len(cell_voltages) == NUM_VOLT_CELLS:
                        rec["bms"]["cell_voltages"] = np.array(cell_voltages, dtype=np.float32)

                    # --- Cell Temperatures ---
                    cell_temp_cols = [f'bms_cell_temps_{i+1}' for i in range(NUM_TEMP_CELLS)]
                    cell_temps = []
                    for col in cell_temp_cols:
                        if col in header and vals[header.index(col)]:
                            cell_temps.append(np.float32(vals[header.index(col)]))
                        else:
                            cell_temps.append(np.float32(0))
                    if len(cell_temps) == NUM_TEMP_CELLS:
                        rec["bms"]["cell_temps"] = np.array(cell_temps, dtype=np.float32)

                    # all other fields (suspension, IMU, GPS, PDM amps, inverter, etc.)
                    # remain at their default zero values
                except (ValueError, IndexError, KeyError) as e:
                    print(f"Error processing row : {vals} - {e}")
                    # Handle the error appropriately

        # print(f"NUMBER OF SNAPSHOTS:{__len__(db)}")
        return db

