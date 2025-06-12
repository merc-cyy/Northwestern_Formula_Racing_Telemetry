#!/usr/bin/env python3
"""
Script to parse a hierarchy text file and emit a YAML mapping from Board.Message.Signal
 to CarSnapshot attribute names (or '???' if unsupported).

Usage:
    python generate_car_mapping.py hierarchy.txt car_mapping.yaml
"""
import sys
import re

# --- Determination logic for CarDB-supported attributes ---


def determine_attr(board, message, signal):
    # BMS mappings
    if board == "BMS":
        # Faults
        if message == "BMS_Faults":
            fault_map = {
                "Fault_Summary": "fault_summary",
                "Undervoltage_Fault": "undervoltage_fault",
                "Overvoltage_Fault": "overvoltage_fault",
                "Undertemperature_Fault": "undertemperature_fault",
                "Overtemperature_Fault": "overtemperature_fault",
                "Overcurrent_Fault": "overcurrent_fault",
                "External_Kill_Fault": "external_kill_fault",
                "Open_Wire_Fault": "open_wire_fault",
                "Open_Wire_Temp_Fault": "open_wire_temp_fault",
                "Pec_Fault": "pec_fault",
                "Total_PEC_Failures": "total_pec_failures",
            }
            return f"bms.{fault_map.get(signal, '???')}"
        # SOE
        if message == "BMS_SOE":
            soe_map = {
                "Max_Discharge_Current": "max_discharge_current",
                "Max_Regen_Current": "max_regen_current",
                "Battery_Voltage": "battery_voltage",
                "Battery_Temperature": "battery_temp",
                "Battery_Current": "battery_current",
            }
            return f"bms.{soe_map.get(signal, '???')}"
        # Status
        if message == "BMS_Status":
            status_map = {
                "BMS_State": "bms_state",
                "IMD_State": "imd_state",
                "Max_Cell_Temp": "max_cell_temp",
                "Min_Cell_Temp": "min_cell_temp",
                "Max_Cell_Voltage": "max_cell_voltage",
                "Min_Cell_Voltage": "min_cell_voltage",
                "BMS_SOC": "soc",
            }
            return f"bms.{status_map.get(signal, '???')}"
        # Temperatures
        m = re.match(r"BMS_Temperatures_(\d+)", message)
        if m:
            # Cell_T_<index>
            idx = int(signal.split("_")[-1]) if signal.startswith("Cell_T_") else None
            return f"bms.cell_temps[{idx}]" if idx is not None else "???"
        # Voltages
        m2 = re.match(r"BMS_Voltages_(\d+)", message)
        if m2:
            # Cell_V_<index>
            if signal.startswith("Cell_V_"):
                idx = int(signal.split("_")[-1])
                return f"bms.cell_voltages[{idx}]"
            # OCV offsets not supported
            if signal.startswith("Cell_OCV_Offset_"):
                return "???"
    # PDM
    if board == "PDM":
        if message == "PDM_Bat_Volt":
            return {
                "Bat_Volt": "pdm.bat_voltage",
                "Bat_Volt_Warning": "pdm.bat_voltage_warning",
            }.get(signal, "???")
        if message == "PDM_Current":
            return {
                "Gen_Amps": "pdm.gen_amps",
                "Fan_Amps": "pdm.fan_amps",
                "Pump_Amps": "pdm.pump_amps",
            }.get(signal, "???")
        if message == "PDM_EFuse_Reset":
            return {
                "Reset_Gen_Efuse": "pdm.reset_gen_efuse",
                "Reset_AC_Efuse": "pdm.reset_ac_efuse",
            }.get(signal, "???")
        if message == "PDM_EFuse_Triggered":
            return {"Gen_EFuse_Triggered": "pdm.gen_efuse_triggered"}.get(signal, "???")
    # Inverter
    if board == "Inverter":
        if message == "Inverter_Current_Draw":
            return {
                "Ah_Drawn": "inverter.ah_drawn",
                "Ah_Charged": "inverter.ah_charged",
            }.get(signal, "???")
        if message == "Inverter_Fault_Status":
            return {"Fault_Code": "inverter.fault_code"}.get(signal, "???")
        if message == "Inverter_Motor_Status":
            return {
                "RPM": "inverter.rpm",
                "Motor_Current": "inverter.motor_current",
                "DC_Voltage": "inverter.dc_voltage",
                "DC_Current": "inverter.dc_current",
            }.get(signal, "???")
        if message == "Inverter_Power_Draw":
            return {
                "Wh_Drawn": "inverter.wh_drawn",
                "Wh_Charged": "inverter.wh_charged",
            }.get(signal, "???")
        if message == "Inverter_Temp_Status":
            return {
                "IGBT_Temp": "inverter.igbt_temp",
                "Motor_Temp": "inverter.motor_temp",
            }.get(signal, "???")
    # ECU
    if board == "ECU":
        if message == "ECU_Active_Aero_Command":
            return {
                "Active_Aero_State": "ecu.active_aero_state",
                "Active_Aero_Position": "ecu.active_aero_position",
            }.get(signal, "???")
        if message == "ECU_BMS_Command_Message":
            return {"BMS_Command": "ecu.bms_command"}.get(signal, "???")
        if message == "ECU_Brake":
            return {
                "Front_Brake_Pressure": "ecu.brake_pressures[0]",
                "Rear_Brake_Pressure": "ecu.brake_pressures[1]",
                "Brake_Pressed": "ecu.brake_pressed",
            }.get(signal, "???")
        if message == "ECU_Drive_Status":
            return {"Drive_State": "ecu.drive_state"}.get(signal, "???")
        if message == "ECU_Implausibility":
            idx_map = {
                "Implausibility_Present": 0,
                "APPSs_Disagreement_Imp": 1,
                "BPPC_Imp": 2,
                "Brake_Invalid_Imp": 3,
                "APPSs_Invalid_Imp": 4,
            }
            idx = idx_map.get(signal)
            return f"ecu.implausibilities[{idx}]" if idx is not None else "???"
        if message == "ECU_LUT_Response":
            return {"Accel_LUT_Id_Response": "ecu.accel_lut_id_response"}.get(
                signal, "???"
            )
        if message == "ECU_Pump_Fan_Command":
            return {
                "Pump_Duty_Cycle": "ecu.pump_duty_cycle",
                "Fan_Duty_Cycle": "ecu.fan_duty_cycle",
            }.get(signal, "???")
        if message == "ECU_Set_Current":
            return {"Set_Current": "ecu.set_current"}.get(signal, "???")
        if message == "ECU_Set_Current_Brake":
            return {"Set_Current_Brake": "ecu.set_current_brake"}.get(signal, "???")
        if message == "ECU_Temp_Limiting_Status":
            return {
                "IGBT_Temp_Limiting": "ecu.igbt_temp_limiting",
                "Battery_Temp_Limiting": "ecu.battery_temp_limiting",
                "Motor_Temp_Limiting": "ecu.motor_temp_limiting",
            }.get(signal, "???")
        if message == "ECU_Throttle":
            return {
                "APPS1_Throttle": "ecu.apps1_throttle",
                "APPS2_Throttle": "ecu.apps2_throttle",
            }.get(signal, "???")
        if message == "ECU_Torque_Status":
            return {"Torque_Status": "ecu.torque_status"}.get(signal, "???")
    # DAQ / Dynamics
    if board.startswith("DAQ-"):
        # IMU acceleration
        if message == "DAQ_Dynamics_IMU_Acceleration":
            comp = {"X_Acceleration": 0, "Y_Acceleration": 1, "Z_Acceleration": 2}
            idx = comp.get(signal)
            return f"dynamics.imu.accel[{idx}]" if idx is not None else "???"
        # Pitot speeds
        if "Dynamics_Pitot_Lower" in message or "Dynamics_Pitot_Upper" in message:
            idx = (
                int(signal.split("_")[-1]) if signal.startswith("Air_Speed_") else None
            )
            return f"dynamics.air_speed[{idx}]" if idx is not None else "???"
        # Steering
        if message == "DAQ_Dynamics_Steering":
            return "dynamics.steering_angle"
        # Coolant temps
        if message == "DAQ_Coolant_Temps":
            if signal == "Before_Motor_Temperature":
                return "dynamics.coolant_temps[0]"
            if signal == "Before_Accumulator_Temperature":
                return "dynamics.coolant_temps[1]"
        # GPS
        if message == "DAQ_GPS":
            return {
                "Latitude": "dynamics.gps_location[0]",
                "Longitude": "dynamics.gps_location[1]",
            }.get(signal, "???")
    # fallback
    return "???"


def main():
    print("Generating mapping...")

    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    in_file, out_file = sys.argv[1], sys.argv[2]
    mapping = {}
    with open(in_file) as f:
        lines = [l.strip() for l in f if l.strip()]
    for line in lines:
        parts = line.split(".")
        if len(parts) != 3:
            continue
        board, message, signal = parts
        mapping.setdefault(board, {}).setdefault(message, {})[signal] = determine_attr(
            board, message, signal
        )
    # write YAML
    with open(out_file, "w") as f:

        def write(d, indent=0):
            for k, v in d.items():
                f.write("  " * indent + f"{k}:\n")
                if isinstance(v, dict):
                    write(v, indent + 1)
                else:
                    f.write("  " * (indent + 1) + f"{v}\n")

        write(mapping)
    print(f"Wrote mapping to {out_file}")


if __name__ == "__main__":
    main()
