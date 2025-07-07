import numpy as np
import csv
from dataclasses import dataclass
from typing import List

# ——— Constants ———
BMS_TEMP_VOLTAGE_COUNT = 140
BMS_TEMP_CELL_COUNT = 80
GPS_COORDS = 2  # e.g. lat, lon


# ——— Python dataclasses for your domain objects ———
@dataclass
class TimeData:
    time_since_startup: int
    hour: int
    minute: int
    second: int
    millis: int


@dataclass
class CornerData:
    wheel_speed: float
    raw_sus_displacement: float
    wheel_displacement: float
    pr_strain: float


@dataclass
class IMUData:
    accel: np.ndarray  # shape (3,)
    vel: np.ndarray  # shape (3,)
    pos: np.ndarray  # shape (3,)
    orientation: np.ndarray  # shape (3,)


@dataclass
class DynamicsData:
    air_speed: np.ndarray  # (8,)
    coolant_temps: np.ndarray  # (2,)
    coolant_flow: float
    steering_angle: float
    imu: IMUData
    gps_location: np.ndarray  # (2,)


@dataclass
class BMSData:
    cell_temps: np.ndarray  # (80,)
    cell_voltages: np.ndarray  # (140,)
    max_discharge_current: float  # BMS_SOE.Max_Discharge_Current
    max_regen_current: float  # BMS_SOE.Max_Regen_Current
    battery_temp: float  # BMS_SOE.Battery_Temperature
    battery_voltage: float  # BMS_SOE.Battery_Voltage
    battery_current: float  # BMS_SOE.Battery_Current
    soc: float  # BMS_Status.BMS_SOC
    bms_state: int  # BMS_Status.BMS_State
    imd_state: int  # BMS_Status.IMD_State
    max_cell_temp: float  # BMS_Status.Max_Cell_Temp
    min_cell_temp: float  # BMS_Status.Min_Cell_Temp
    max_cell_voltage: float  # BMS_Status.Max_Cell_Voltage
    min_cell_voltage: float  # BMS_Status.Min_Cell_Voltage
    fault_summary: int  # BMS_Faults.Fault_Summary
    undervoltage_fault: bool  # BMS_Faults.Undervoltage_Fault
    overvoltage_fault: bool  # BMS_Faults.Overvoltage_Fault
    undertemperature_fault: bool  # BMS_Faults.Undertemperature_Fault
    overtemperature_fault: bool  # BMS_Faults.Overtemperature_Fault
    overcurrent_fault: bool  # BMS_Faults.Overcurrent_Fault
    external_kill_fault: bool  # BMS_Faults.External_Kill_Fault
    open_wire_fault: bool  # BMS_Faults.Open_Wire_Fault
    open_wire_temp_fault: bool  # BMS_Faults.Open_Wire_Temp_Fault
    pec_fault: bool  # BMS_Faults.Pec_Fault
    total_pec_failures: int  # BMS_Faults.Total_PEC_Failures


@dataclass
class PDMData:
    gen_amps: float  # current of the generator
    fan_amps: float  # current of the cooling fan
    pump_amps: float  # current of the pump
    bat_voltage: float  # battery voltage
    bat_voltage_warning: bool  # PDM_Bat_Volt_Warning
    gen_efuse_triggered: bool  # PDM_EFuse_Triggered.Gen_EFuse_Triggered
    fan_efuse_triggered: bool  # PDM_EFuse_Triggered.Fan_EFuse_Triggered
    pump_efuse_triggered: bool  # PDM_EFuse_Triggered.Pump_EFuse_Triggered
    reset_gen_efuse: bool  # PDM_EFuse_Reset.Reset_Gen_Efuse
    reset_ac_efuse: bool  # PDM_EFuse_Reset.Reset_AC_Efuse


@dataclass
class InverterData:
    rpm: float
    motor_current: float
    dc_voltage: float
    dc_current: float
    igbt_temp: float
    motor_temp: float
    ah_drawn: float
    ah_charged: float
    wh_drawn: float
    wh_charged: float
    fault_code: float


@dataclass
class ECUData:
    apps_positions: np.ndarray  # (2,)
    brake_pressures: np.ndarray  # (2,)
    brake_pressed: float
    drive_state: int
    implausibilities: np.ndarray  # (5,)
    bms_command: int  # ECU_BMS_Command_Message.BMS_Command
    active_aero_state: int  # ECU_Active_Aero_Command.Active_Aero_State
    active_aero_position: float  # ECU_Active_Aero_Command.Active_Aero_Position
    pump_duty_cycle: float  # ECU_Pump_Fan_Command.Pump_Duty_Cycle
    fan_duty_cycle: float  # ECU_Pump_Fan_Command.Fan_Duty_Cycle
    set_current: float  # ECU_Set_Current.Set_Current
    set_current_brake: float  # ECU_Set_Current_Brake.Set_Current_Brake
    accel_lut_id_response: int  # ECU_LUT_Response.Accel_LUT_Id_Response
    igbt_temp_limiting: bool  # ECU_Temp_Limiting_Status.IGBT_Temp_Limiting
    battery_temp_limiting: bool  # ECU_Temp_Limiting_Status.Battery_Temp_Limiting
    motor_temp_limiting: bool  # ECU_Temp_Limiting_Status.Motor_Temp_Limiting
    apps1_throttle: float  # ECU_Throttle.APPS1_Throttle
    apps2_throttle: float  # ECU_Throttle.APPS2_Throttle
    torque_status: int  # ECU_Torque_Status.Torque_Status


@dataclass
class CarSnapshot:
    time: TimeData
    corners: List[CornerData]
    dynamics: DynamicsData
    bms: BMSData
    pdm: PDMData
    inverter: InverterData
    ecu: ECUData


# ——— NumPy dtypes for fast storage and CSV flattening ———
time_dtype = np.dtype(
    [
        ("time_since_startup", "u4"),
        ("unix_time", "u4"),
        ("hour", "u1"),
        ("minute", "u1"),
        ("second", "u1"),
        ("millis", "u2"),
    ]
)

corner_dtype = np.dtype(
    [
        ("wheel_speed", "f4"),
        ("raw_sus_displacement", "f4"),
        ("wheel_displacement", "f4"),
        ("pr_strain", "f4"),
        ("wheel_temperature", "f4", 8),
    ]
)

imu_dtype = np.dtype(
    [
        ("accel", "f4", 3),
        ("vel", "f4", 3),
        ("pos", "f4", 3),
        ("orientation", "f4", 3),
    ]
)

dynamics_dtype = np.dtype(
    [
        ("air_speed", "f4", 8),
        ("coolant_temps", "f4", 2),
        ("coolant_flow", "f4"),
        ("steering_angle", "f4"),
        ("imu", imu_dtype),
        ("gps_location", "f8", GPS_COORDS),
    ]
)

bms_dtype = np.dtype(
    [
        ("cell_temps", "f4", BMS_TEMP_CELL_COUNT),
        ("cell_voltages", "f4", BMS_TEMP_VOLTAGE_COUNT),
        ("max_discharge_current", "f4"),
        ("max_regen_current", "f4"),
        ("battery_temp", "f4"),
        ("battery_voltage", "f4"),
        ("battery_current", "f4"),
        ("soc", "f4"),
        ("bms_state", "i4"),
        ("imd_state", "i4"),
        ("max_cell_temp", "f4"),
        ("min_cell_temp", "f4"),
        ("max_cell_voltage", "f4"),
        ("min_cell_voltage", "f4"),
        ("fault_summary", "?"),
        ("undervoltage_fault", "?"),
        ("overvoltage_fault", "?"),
        ("undertemperature_fault", "?"),
        ("overtemperature_fault", "?"),
        ("overcurrent_fault", "?"),
        ("external_kill_fault", "?"),
        ("open_wire_fault", "?"),
        ("open_wire_temp_fault", "?"),
        ("pec_fault", "?"),
        ("total_pec_failures", "i4"),
    ]
)

pdm_dtype = np.dtype(
    [
        ("gen_amps", "f4"),
        ("fan_amps", "f4"),
        ("pump_amps", "f4"),
        ("bat_voltage", "f4"),
        ("bat_voltage_warning", "?"),
        ("gen_efuse_triggered", "?"),
        ("fan_efuse_triggered", "?"),
        ("pump_efuse_triggered", "?"),
        ("reset_gen_efuse", "?"),
        ("reset_ac_efuse", "?"),
    ]
)

inverter_dtype = np.dtype(
    [
        ("rpm", "f4"),
        ("motor_current", "f4"),
        ("dc_voltage", "f4"),
        ("dc_current", "f4"),
        ("igbt_temp", "f4"),
        ("motor_temp", "f4"),
        ("ah_drawn", "f4"),
        ("ah_charged", "f4"),
        ("wh_drawn", "f4"),
        ("wh_charged", "f4"),
        ("fault_code", "f4"),
    ]
)

ecu_dtype = np.dtype(
    [
        ("apps_positions", "f4", 2),
        ("brake_pressures", "f4", 2),
        ("brake_pressed", "f4"),
        ("drive_state", "i4"),
        ("implausibilities", "?", 5),
        ("bms_command", "i4"),
        ("active_aero_state", "i4"),
        ("active_aero_position", "f4"),
        ("pump_duty_cycle", "f4"),
        ("fan_duty_cycle", "f4"),
        ("set_current", "f4"),
        ("set_current_brake", "f4"),
        ("accel_lut_id_response", "i4"),
        ("igbt_temp_limiting", "?"),
        ("battery_temp_limiting", "?"),
        ("motor_temp_limiting", "?"),
        ("apps1_throttle", "f4"),
        ("apps2_throttle", "f4"),
        ("torque_status", "i4"),
    ]
)

car_snapshot_dtype = np.dtype(
    [
        ("time", time_dtype),
        ("corners", corner_dtype, 4),
        ("dynamics", dynamics_dtype),
        ("bms", bms_dtype),
        ("pdm", pdm_dtype),
        ("inverter", inverter_dtype),
        ("ecu", ecu_dtype),
    ]
)


class CarDB:
    def __init__(self, n_snapshots: int):
        print(f"Creating database with {n_snapshots} snapshots!")
        self._db = np.zeros(n_snapshots, dtype=car_snapshot_dtype)

    def __len__(self):
        return len(self._db)

    def raw_record(self, idx: int) -> np.void:
        return self._db[idx]

    def get_snapshot(self, idx: int) -> CarSnapshot:
        # Convert raw numpy record to CarSnapshot instance
        rec = self._db[idx]
        time = TimeData(**rec["time"].tolist())
        corners = [CornerData(*tuple(rec["corners"][i])) for i in range(4)]
        imu = IMUData(
            rec["dynamics"]["imu"]["accel"],
            rec["dynamics"]["imu"]["vel"],
            rec["dynamics"]["imu"]["pos"],
            rec["dynamics"]["imu"]["orientation"],
        )
        dynamics = DynamicsData(
            rec["dynamics"]["air_speed"],
            rec["dynamics"]["coolant_temps"],
            rec["dynamics"]["coolant_flow"],
            rec["dynamics"]["steering_angle"],
            imu,
            rec["dynamics"]["gps_location"],
        )
        bms = BMSData(**{k: rec["bms"][k] for k in rec["bms"].dtype.names})
        pdm = PDMData(**{k: rec["pdm"][k] for k in rec["pdm"].dtype.names})
        inverter = InverterData(
            **{k: rec["inverter"][k] for k in rec["inverter"].dtype.names}
        )
        ecu = ECUData(**{k: rec["ecu"][k] for k in rec["ecu"].dtype.names})
        return CarSnapshot(time, corners, dynamics, bms, pdm, inverter, ecu)

    def to_csv(self, path: str) -> None:
        """
        Flatten all snapshots into a CSV file.  Arrays and nested structs
        become separate columns (e.g. corners0_wheel_speed, dynamics_imu_accel_2, ...).
        """
        rows = []
        for rec in self._db:  # for each record,
            flat = {}  # just a dictionary with key(the col) = value(data)
            for name in rec.dtype.names:
                val = rec[name]  # get the values
                # nested structured dtype
                if val.dtype.fields is not None:

                    def flatten_struct(v, prefix):  # flatten the subfields
                        d = {}
                        for fn in v.dtype.names:  # iterate through the names
                            v2 = v[fn]  # get val
                            if isinstance(v2, np.ndarray):
                                for i, x in enumerate(v2.tolist()):
                                    d[f"{prefix}_{fn}_{i}"] = x
                            else:
                                d[f"{prefix}_{fn}"] = (
                                    v2.item() if hasattr(v2, "item") else v2
                                )
                        return d  # returns dict with flatten data of that sub field

                    if isinstance(val, np.ndarray):
                        for j, sub in enumerate(val):
                            flat.update(flatten_struct(sub, f"{name}{j}"))
                    else:
                        flat.update(flatten_struct(val, name))

                # plain numpy array or scalar
                else:
                    if isinstance(val, np.ndarray):
                        for i, x in enumerate(val.tolist()):
                            flat[f"{name}_{i}"] = x
                    else:
                        flat[name] = val.item() if hasattr(val, "item") else val

            rows.append(flat)  # add the flattened data to the row

        # write CSV
        if rows:
            fieldnames = sorted(rows[0].keys())
            with open(path, "w", newline="") as csvfile:
                writer = csv.DictWriter(
                    csvfile, fieldnames=fieldnames
                )  # adds the row to the csv file
                writer.writeheader()
                writer.writerows(rows)
