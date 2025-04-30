import numpy as np
import csv
from dataclasses import dataclass
from typing import List, Optional

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
    cell_temps: np.ndarray  # (BMS_TEMP_CELL_COUNT,)
    cell_voltages: np.ndarray  # (BMS_TEMP_VOLTAGE_COUNT,)
    soe_max_discharge_current: float
    soe_max_regen_current: float
    soe_bat_temp: float
    soe_bat_voltage: float
    soe_bat_current: float
    faults: np.ndarray  # (8,) of bools
    bms_state: int


@dataclass
class PDMData:
    gen_amps: float
    fan_amps: float
    pump_amps: float
    bat_voltage: float
    bat_voltage_warning: bool
    gen_efuse_triggered: bool
    fan_efuse_triggered: bool
    pump_efuse_triggered: bool


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
    implausibilities: np.ndarray  # (5,) of bools


@dataclass
class CarSnapshot:
    time: TimeData
    corners: List[CornerData]  # length 4
    dynamics: DynamicsData
    bms: BMSData
    pdm: PDMData
    inverter: InverterData
    ecu: ECUData


# ——— Build the identical NumPy dtype under the hood ———
time_dtype = np.dtype(
    [
        ("time_since_startup", "u4"),
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
        ("soe_max_discharge_current", "f4"),
        ("soe_max_regen_current", "f4"),
        ("soe_bat_temp", "f4"),
        ("soe_bat_voltage", "f4"),
        ("soe_bat_current", "f4"),
        ("faults", "?", 8),
        ("bms_state", "i4"),
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


# ——— The CarDB class with CSV export ———
class CarDB:
    def __init__(self, n_snapshots: int):
        self._db = np.zeros(n_snapshots, dtype=car_snapshot_dtype)

    def __len__(self):
        return len(self._db)

    def raw_record(self, idx: int) -> np.void:
        return self._db[idx]

    def get_snapshot(self, idx: int) -> CarSnapshot:
        # ... existing get_snapshot code omitted for brevity ...
        pass

    def to_csv(self, path: str) -> None:
        """
        Flatten all snapshots into a CSV file.  Arrays and nested structs
        become separate columns (e.g. corners0_wheel_speed, dynamics_imu_accel_2, ...).
        """
        rows = []
        for rec in self._db:
            flat = {}
            for name in rec.dtype.names:
                val = rec[name]
                # nested structured dtype
                if val.dtype.fields is not None:

                    def flatten_struct(v, prefix):
                        d = {}
                        for fn in v.dtype.names:
                            v2 = v[fn]
                            if isinstance(v2, np.ndarray):
                                for i, x in enumerate(v2.tolist()):
                                    d[f"{prefix}_{fn}_{i}"] = x
                            else:
                                d[f"{prefix}_{fn}"] = (
                                    v2.item() if hasattr(v2, "item") else v2
                                )
                        return d

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

            rows.append(flat)

        # write CSV
        if rows:
            fieldnames = sorted(rows[0].keys())
            with open(path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
