import numpy as np


class CornerData:
    wheel_speed: float
    raw_sus_displacement: float
    wheel_displacement: float
    pr_strain: float


class IMUData:
    accel: np.array  # vec3
    vel: np.array  # vec3
    pos: np.array  # vec3
    orientaiton: np.array  # vec3


class DynamicsData:
    air_speed: np.array  # vec8
    coolant_temps: np.array  # vec2
    coolant_flow: float
    steering_angle: float
    imu: IMUData
    gps_location: np.array


class BMSData:
    cell_temps: np.array  # array of cell temperatures
    cell_voltages: np.array  # array of cell voltages
    soe_max_discharge_current: float
    soe_max_regen_current: float
    soe_bat_temp: float
    soe_bat_voltage: float
    soe_bat_current: float
    faults: np.array  # 8 bools
    bms_state: int


class PDMData:
    gen_amps: float
    fan_amps: float
    pump_amps: float
    bat_voltage: float
    bat_voltage_warning: bool
    gen_efuse_triggered: bool
    fan_efuse_triggered: bool
    pump_efuse_triggered: bool


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


class ECUData:
    apps_positions: np.array  # two positions (float)
    brake_pressures: np.array  # front/back
    brake_pressed: float
    drive_state: int
    implausibilities: np.array  # 5 bools

class TimeData:
    time_since_startup : int
    hour : int
    minute : int
    second : int
    millis : int

class CarSnapshot:
    time : TimeData
    corners: np.array  # 4 corners
    dynamics: DynamicsData
    ecu : ECUData
    pdm : PDMData
    inverter : InverterData


class CarDB:
    snapshots: np.array  # array of CarSnapshots
