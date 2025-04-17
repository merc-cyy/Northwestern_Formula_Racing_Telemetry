from dataclasses import dataclass
from typing import List, Optional
import numpy as np

# ——— Constants ———
BMS_CELL_COUNT = 12
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
    cell_temps: np.ndarray  # (BMS_CELL_COUNT,)
    cell_voltages: np.ndarray  # (BMS_CELL_COUNT,)
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
        ("cell_temps", "f4", BMS_CELL_COUNT),
        ("cell_voltages", "f4", BMS_CELL_COUNT),
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


# ——— The CarDB class ———
class CarDB:
    def __init__(self, n_snapshots: int):
        self._db = np.zeros(n_snapshots, dtype=car_snapshot_dtype)

    def __len__(self):
        return len(self._db)

    def raw_record(self, idx: int) -> np.void:
        return self._db[idx]

    def get_snapshot(self, idx: int) -> CarSnapshot:
        rec = self._db[idx]
        # unpack TimeData
        t = rec["time"]
        time = TimeData(
            time_since_startup=int(t["time_since_startup"]),
            hour=int(t["hour"]),
            minute=int(t["minute"]),
            second=int(t["second"]),
            millis=int(t["millis"]),
        )
        # unpack corners
        corners = []
        for c in rec["corners"]:
            corners.append(
                CornerData(
                    wheel_speed=float(c["wheel_speed"]),
                    raw_sus_displacement=float(c["raw_sus_displacement"]),
                    wheel_displacement=float(c["wheel_displacement"]),
                    pr_strain=float(c["pr_strain"]),
                )
            )
        # unpack dynamics / IMU
        d = rec["dynamics"]
        imu = d["imu"]
        imu_obj = IMUData(
            accel=imu["accel"].copy(),
            vel=imu["vel"].copy(),
            pos=imu["pos"].copy(),
            orientation=imu["orientation"].copy(),
        )
        dynamics = DynamicsData(
            air_speed=d["air_speed"].copy(),
            coolant_temps=d["coolant_temps"].copy(),
            coolant_flow=float(d["coolant_flow"]),
            steering_angle=float(d["steering_angle"]),
            imu=imu_obj,
            gps_location=d["gps_location"].copy(),
        )
        # unpack BMS
        b = rec["bms"]
        bms = BMSData(
            cell_temps=b["cell_temps"].copy(),
            cell_voltages=b["cell_voltages"].copy(),
            soe_max_discharge_current=float(b["soe_max_discharge_current"]),
            soe_max_regen_current=float(b["soe_max_regen_current"]),
            soe_bat_temp=float(b["soe_bat_temp"]),
            soe_bat_voltage=float(b["soe_bat_voltage"]),
            soe_bat_current=float(b["soe_bat_current"]),
            faults=b["faults"].copy(),
            bms_state=int(b["bms_state"]),
        )
        # unpack PDM
        p = rec["pdm"]
        pdm = PDMData(
            gen_amps=float(p["gen_amps"]),
            fan_amps=float(p["fan_amps"]),
            pump_amps=float(p["pump_amps"]),
            bat_voltage=float(p["bat_voltage"]),
            bat_voltage_warning=bool(p["bat_voltage_warning"]),
            gen_efuse_triggered=bool(p["gen_efuse_triggered"]),
            fan_efuse_triggered=bool(p["fan_efuse_triggered"]),
            pump_efuse_triggered=bool(p["pump_efuse_triggered"]),
        )
        # unpack Inverter
        i = rec["inverter"]
        inverter = InverterData(
            rpm=float(i["rpm"]),
            motor_current=float(i["motor_current"]),
            dc_voltage=float(i["dc_voltage"]),
            dc_current=float(i["dc_current"]),
            igbt_temp=float(i["igbt_temp"]),
            motor_temp=float(i["motor_temp"]),
            ah_drawn=float(i["ah_drawn"]),
            ah_charged=float(i["ah_charged"]),
            wh_drawn=float(i["wh_drawn"]),
            wh_charged=float(i["wh_charged"]),
            fault_code=float(i["fault_code"]),
        )
        # unpack ECU
        e = rec["ecu"]
        ecu = ECUData(
            apps_positions=e["apps_positions"].copy(),
            brake_pressures=e["brake_pressures"].copy(),
            brake_pressed=float(e["brake_pressed"]),
            drive_state=int(e["drive_state"]),
            implausibilities=e["implausibilities"].copy(),
        )

        return CarSnapshot(
            time=time,
            corners=corners,
            dynamics=dynamics,
            bms=bms,
            pdm=pdm,
            inverter=inverter,
            ecu=ecu,
        )

    def find_by_startup_time(self, t0: int) -> Optional[int]:
        idxs = np.nonzero(self._db["time"]["time_since_startup"] == t0)[0]
        return int(idxs[0]) if idxs.size else None

    # ——— More convenience readers ———

    def wheel_speeds(self, idx: int) -> List[float]:
        """All four corner wheel speeds for snapshot idx."""
        return [float(c["wheel_speed"]) for c in self._db[idx]["corners"]]

    def imu_acceleration(self, idx: int) -> np.ndarray:
        return self._db[idx]["dynamics"]["imu"]["accel"].copy()

    def gps_location(self, idx: int) -> np.ndarray:
        return self._db[idx]["dynamics"]["gps_location"].copy()
