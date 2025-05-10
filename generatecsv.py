import csv
import random
import time
import numpy as np

def generate_plausible_bms_state():
    return random.choice([0, 1, 2, 3])  # Representing IDLE, CHARGING, DISCHARGING, FAULT as integers

def generate_plausible_cell_temp():
    return round(random.uniform(15.0, 45.0), 1)

def generate_plausible_cell_voltage():
    return round(random.uniform(3.0, 4.2), 3)

def generate_plausible_fault():
    return random.choice([False, True])

def generate_plausible_current():
    return round(random.uniform(-100.0, 150.0), 1)

def generate_plausible_temp():
    return round(random.uniform(10.0, 50.0), 1)

def generate_plausible_voltage():
    return round(random.uniform(300.0, 450.0), 1)

def generate_plausible_strain():
    return round(random.uniform(-0.001, 0.001), 6)

def generate_plausible_displacement():
    return round(random.uniform(-0.05, 0.05), 4)

def generate_plausible_wheel_speed():
    return round(random.uniform(0.0, 150.0), 1)

def generate_plausible_air_speed():
    return round(random.uniform(0.0, 80.0), 1)

def generate_plausible_coolant_flow():
    return round(random.uniform(0.0, 10.0), 2)

def generate_plausible_coolant_temp():
    return round(random.uniform(20.0, 100.0), 1)

def generate_plausible_gps():
    lat = round(random.uniform(40.0, 43.0), 6)
    lon = round(random.uniform(-88.0, -87.0), 6)
    return f"({lat}, {lon})"

def generate_plausible_imu():
    # Keep the original structure, but ensure float32
    return f"(array([{', '.join(map(str, np.random.rand(3).round(3)))}], dtype=float32), array([{', '.join(map(str, np.random.rand(3).round(3)))}], dtype=float32), array([{', '.join(map(str, np.random.rand(3).round(3)))}], dtype=float32), array([{', '.join(map(str, np.random.rand(3).round(3)))}], dtype=float32))"


def generate_plausible_steering_angle():
    return round(random.uniform(-45.0, 45.0), 1)

def generate_plausible_app_position():
    return round(random.uniform(0.0, 100.0), 1)

def generate_plausible_brake_pressure():
    return round(random.uniform(0.0, 1500.0), 1)

def generate_plausible_drive_state():
    return random.choice([0, 1, 2])  # Representing FORWARD, REVERSE, NEUTRAL as integers

def generate_plausible_ah():
    return round(random.uniform(0.0, 200.0), 2)

def generate_plausible_wh():
    return round(random.uniform(0.0, 800.0), 2)

def generate_plausible_rpm():
    return int(round(random.uniform(0.0, 10000.0), 0))

def generate_plausible_fault_code():
    return random.randint(0, 255)

def generate_plausible_fan_amp():
    return round(random.uniform(0.0, 5.0), 1)

def generate_plausible_gen_amp():
    return round(random.uniform(-10.0, 10.0), 1)

def generate_plausible_pump_amp():
    return round(random.uniform(0.0, 3.0), 1)

def generate_plausible_time():
    now = time.localtime()
    hour = np.uint8(now.tm_hour)
    minute = np.uint8(now.tm_min)
    second = np.uint8(now.tm_sec)
    millis = np.uint16(int(time.time() * 1000) % 1000)
    time_since_startup = np.uint32(int(time.time() * 1000))
    return hour, millis, minute, second, time_since_startup

headers = [
    "bms_bms_state", "bms_cell_temps_0", "bms_cell_temps_1", "bms_cell_temps_10", "bms_cell_temps_11", "bms_cell_temps_12", "bms_cell_temps_13", "bms_cell_temps_14", "bms_cell_temps_15", "bms_cell_temps_16", "bms_cell_temps_17", "bms_cell_temps_18", "bms_cell_temps_19", "bms_cell_temps_2", "bms_cell_temps_20", "bms_cell_temps_21", "bms_cell_temps_22", "bms_cell_temps_23", "bms_cell_temps_24", "bms_cell_temps_25", "bms_cell_temps_26", "bms_cell_temps_27", "bms_cell_temps_28", "bms_cell_temps_29", "bms_cell_temps_3", "bms_cell_temps_30", "bms_cell_temps_31", "bms_cell_temps_32", "bms_cell_temps_33", "bms_cell_temps_34", "bms_cell_temps_35", "bms_cell_temps_36", "bms_cell_temps_37", "bms_cell_temps_38", "bms_cell_temps_39", "bms_cell_temps_4", "bms_cell_temps_40", "bms_cell_temps_41", "bms_cell_temps_42", "bms_cell_temps_43", "bms_cell_temps_44", "bms_cell_temps_45", "bms_cell_temps_46", "bms_cell_temps_47", "bms_cell_temps_48", "bms_cell_temps_49", "bms_cell_temps_5", "bms_cell_temps_50", "bms_cell_temps_51", "bms_cell_temps_52", "bms_cell_temps_53", "bms_cell_temps_54", "bms_cell_temps_55", "bms_cell_temps_56", "bms_cell_temps_57", "bms_cell_temps_58", "bms_cell_temps_59", "bms_cell_temps_6", "bms_cell_temps_60", "bms_cell_temps_61", "bms_cell_temps_62", "bms_cell_temps_63", "bms_cell_temps_64", "bms_cell_temps_65", "bms_cell_temps_66", "bms_cell_temps_67", "bms_cell_temps_68", "bms_cell_temps_69", "bms_cell_temps_7", "bms_cell_temps_70", "bms_cell_temps_71", "bms_cell_temps_72", "bms_cell_temps_73", "bms_cell_temps_74", "bms_cell_temps_75", "bms_cell_temps_76", "bms_cell_temps_77", "bms_cell_temps_78", "bms_cell_temps_79", "bms_cell_temps_8", "bms_cell_temps_9", "bms_cell_voltages_0", "bms_cell_voltages_1", "bms_cell_voltages_10", "bms_cell_voltages_100", "bms_cell_voltages_101", "bms_cell_voltages_102", "bms_cell_voltages_103", "bms_cell_voltages_104", "bms_cell_voltages_105", "bms_cell_voltages_106", "bms_cell_voltages_107", "bms_cell_voltages_108", "bms_cell_voltages_109", "bms_cell_voltages_11", "bms_cell_voltages_110", "bms_cell_voltages_111", "bms_cell_voltages_112", "bms_cell_voltages_113", "bms_cell_voltages_114", "bms_cell_voltages_115", "bms_cell_voltages_116", "bms_cell_voltages_117", "bms_cell_voltages_118", "bms_cell_voltages_119", "bms_cell_voltages_12", "bms_cell_voltages_120", "bms_cell_voltages_121", "bms_cell_voltages_122", "bms_cell_voltages_123", "bms_cell_voltages_124", "bms_cell_voltages_125", "bms_cell_voltages_126", "bms_cell_voltages_127", "bms_cell_voltages_128", "bms_cell_voltages_129", "bms_cell_voltages_13", "bms_cell_voltages_130", "bms_cell_voltages_131", "bms_cell_voltages_132", "bms_cell_voltages_133", "bms_cell_voltages_134", "bms_cell_voltages_135", "bms_cell_voltages_136", "bms_cell_voltages_137", "bms_cell_voltages_138", "bms_cell_voltages_139", "bms_cell_voltages_14", "bms_cell_voltages_15", "bms_cell_voltages_16", "bms_cell_voltages_17", "bms_cell_voltages_18", "bms_cell_voltages_19", "bms_cell_voltages_2", "bms_cell_voltages_20", "bms_cell_voltages_21", "bms_cell_voltages_22", "bms_cell_voltages_23", "bms_cell_voltages_24", "bms_cell_voltages_25", "bms_cell_voltages_26", "bms_cell_voltages_27", "bms_cell_voltages_28", "bms_cell_voltages_29", "bms_cell_voltages_3", "bms_cell_voltages_30", "bms_cell_voltages_31", "bms_cell_voltages_32", "bms_cell_voltages_33", "bms_cell_voltages_34", "bms_cell_voltages_35", "bms_cell_voltages_36", "bms_cell_voltages_37", "bms_cell_voltages_38", "bms_cell_voltages_39", "bms_cell_voltages_4", "bms_cell_voltages_40", "bms_cell_voltages_41", "bms_cell_voltages_42", "bms_cell_voltages_43", "bms_cell_voltages_44", "bms_cell_voltages_45", "bms_cell_voltages_46", "bms_cell_voltages_47", "bms_cell_voltages_48", "bms_cell_voltages_49", "bms_cell_voltages_5", "bms_cell_voltages_50", "bms_cell_voltages_51", "bms_cell_voltages_52", "bms_cell_voltages_53", "bms_cell_voltages_54", "bms_cell_voltages_55", "bms_cell_voltages_56", "bms_cell_voltages_57", "bms_cell_voltages_58", "bms_cell_voltages_59", "bms_cell_voltages_6", "bms_cell_voltages_60", "bms_cell_voltages_61", "bms_cell_voltages_62", "bms_cell_voltages_63", "bms_cell_voltages_64", "bms_cell_voltages_65", "bms_cell_voltages_66", "bms_cell_voltages_67", "bms_cell_voltages_68", "bms_cell_voltages_69", "bms_cell_voltages_7", "bms_cell_voltages_70", "bms_cell_voltages_71", "bms_cell_voltages_72", "bms_cell_voltages_73", "bms_cell_voltages_74", "bms_cell_voltages_75", "bms_cell_voltages_76", "bms_cell_voltages_77", "bms_cell_voltages_78", "bms_cell_voltages_79", "bms_cell_voltages_8", "bms_cell_voltages_80", "bms_cell_voltages_81", "bms_cell_voltages_82", "bms_cell_voltages_83", "bms_cell_voltages_84", "bms_cell_voltages_85", "bms_cell_voltages_86", "bms_cell_voltages_87", "bms_cell_voltages_88", "bms_cell_voltages_89", "bms_cell_voltages_9", "bms_cell_voltages_90", "bms_cell_voltages_91", "bms_cell_voltages_92", "bms_cell_voltages_93", "bms_cell_voltages_94", "bms_cell_voltages_95", "bms_cell_voltages_96", "bms_cell_voltages_97", "bms_cell_voltages_98", "bms_cell_voltages_99", "bms_faults_0", "bms_faults_1", "bms_faults_2", "bms_faults_3", "bms_faults_4", "bms_faults_5", "bms_faults_6", "bms_faults_7", "bms_soe_bat_current", "bms_soe_bat_temp", "bms_soe_bat_voltage", "bms_soe_max_discharge_current", "bms_soe_max_regen_current", "corners0_pr_strain", "corners0_raw_sus_displacement", "corners0_wheel_displacement", "corners0_wheel_speed", "corners1_pr_strain", "corners1_raw_sus_displacement", "corners1_wheel_displacement", "corners1_wheel_speed", "corners2_pr_strain", "corners2_raw_sus_displacement", "corners2_wheel_displacement", "corners2_wheel_speed", "corners3_pr_strain", "corners3_raw_sus_displacement", "corners3_wheel_displacement", "corners3_wheel_speed", "dynamics_air_speed_0", "dynamics_air_speed_1", "dynamics_air_speed_2", "dynamics_air_speed_3", "dynamics_air_speed_4", "dynamics_air_speed_5", "dynamics_air_speed_6", "dynamics_air_speed_7", "dynamics_coolant_flow", "dynamics_coolant_temps_0", "dynamics_coolant_temps_1", "dynamics_gps_location_0", "dynamics_gps_location_1", "dynamics_imu", "dynamics_steering_angle", "ecu_apps_positions_0", "ecu_apps_positions_1", "ecu_brake_pressed", "ecu_brake_pressures_0", "ecu_brake_pressures_1", "ecu_drive_state", "ecu_implausibilities_0", "ecu_implausibilities_1", "ecu_implausibilities_2", "ecu_implausibilities_3", "ecu_implausibilities_4", "inverter_ah_charged", "inverter_ah_drawn", "inverter_dc_current", "inverter_dc_voltage", "inverter_fault_code", "inverter_igbt_temp", "inverter_motor_current", "inverter_motor_temp", "inverter_rpm", "inverter_wh_charged", "inverter_wh_drawn", "pdm_bat_voltage", "pdm_bat_voltage_warning", "pdm_fan_amps", "pdm_fan_efuse_triggered", "pdm_gen_amps", "pdm_gen_efuse_triggered", "pdm_pump_amps", "pdm_pump_efuse_triggered", "time_hour", "time_millis", "time_minute", "time_second", "time_time_since_startup"
]

def generate_csv_data(filename="synthetic_car_data.csv", num_rows=7500):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for _ in range(num_rows):
            hour, millis, minute, second, time_since_startup = generate_plausible_time()
            row = [
                generate_plausible_bms_state(),
                *[generate_plausible_cell_temp() for _ in range(80)],
                *[generate_plausible_cell_voltage() for _ in range(140)],
                *[generate_plausible_fault() for _ in range(8)],
                generate_plausible_current(),
                generate_plausible_temp(),
                generate_plausible_voltage(),
                generate_plausible_current(),
                generate_plausible_current(),
                *[generate_plausible_strain() for _ in range(4)],
                *[generate_plausible_displacement() for _ in range(4)],
                *[generate_plausible_displacement() for _ in range(4)],
                *[generate_plausible_wheel_speed() for _ in range(4)],
                *[generate_plausible_air_speed() for _ in range(8)],
                generate_plausible_coolant_flow(),
                generate_plausible_coolant_temp(),
                generate_plausible_coolant_temp(),
                generate_plausible_gps(),
                generate_plausible_gps(),
                generate_plausible_imu(),
                generate_plausible_steering_angle(),
                generate_plausible_app_position(),
                generate_plausible_app_position(),
                generate_plausible_fault(),
                generate_plausible_brake_pressure(),
                generate_plausible_brake_pressure(),
                generate_plausible_drive_state(),
                *[generate_plausible_fault() for _ in range(5)],
                generate_plausible_ah(),
                generate_plausible_ah(),
                generate_plausible_current(),
                generate_plausible_voltage(),
                generate_plausible_fault_code(),
                generate_plausible_temp(),
                generate_plausible_current(),
                generate_plausible_temp(),
                generate_plausible_rpm(),
                generate_plausible_wh(),
                generate_plausible_wh(),
                generate_plausible_voltage(),
                generate_plausible_fault(),
                generate_plausible_fan_amp(),
                generate_plausible_fault(),
                generate_plausible_gen_amp(),
                generate_plausible_fault(),
                generate_plausible_pump_amp(),
                generate_plausible_fault(),
                hour,
                millis,
                minute,
                second,
                time_since_startup
            ]
            writer.writerow(row)

if __name__ == "__main__":
    generate_csv_data()
    print("Generated synthetic_car_data.csv")