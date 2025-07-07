# Auto-generated from struct cellVoltages
import struct

def validate_size():
    c_size = 1600
    py_size = struct.calcsize(fmt)
    assert c_size == py_size, f"Size mismatch: C={c_size}, Python={py_size}"

fmt = ''.join([
    '<',  # little-endian, standard alignment
    '8?', # bmsFaults[8] : bool
    '5?', # ecuFaults[5] : bool
    '3x', # pad 3 bytes before hvVoltage
    'f', # hvVoltage : float
    'f', # lvVoltage : float
    'f', # batteryTemp : float
    'f', # maxCellTemp : float
    'f', # minCellTemp : float
    'f', # maxCellVoltage : float
    'f', # minCellVoltage : float
    'f', # maxDischargeCurrent : float
    'f', # maxRegenCurrent : float
    'f', # bmsSOC : float
    '4f', # wheelSpeeds[4] : float
    '4f', # wheelDisplacement[4] : float
    '4f', # prStrain[4] : float
    'f', # genAmps : float
    'f', # fanAmps : float
    'f', # pumpAmps : float
    'H', # bmsFaultsRaw : uint16_t
    'h', # motorRPM : int16_t
    'h', # motorCurrent : int16_t
    'h', # motorDCVoltage : int16_t
    'h', # motorDCCurrent : int16_t
    'h', # frontBrakePressure : int16_t
    'h', # rearBreakPressure : int16_t
    'h', # apps1 : int16_t
    'h', # apps2 : int16_t
    'H', # inverterIGBTTemp : uint16_t
    'H', # inverterMotorTemp : uint16_t
    'B', # driveState : uint8_t
    'B', # bmsState : uint8_t
    'B', # imdState : uint8_t
    'B', # inverterStatus : uint8_t
    'B', # bmsCommand : uint8_t
    '?', # brakePressed : bool
    '?', # lvVoltageWarning : bool
    '?', # pdmGenEfuseTriggered : bool
    '?', # pdmACEfuseTriggered : bool
    '1x', # pad 1 bytes before inverterAhDrawn
    'I', # inverterAhDrawn : uint32_t
    'I', # inverterAhCharged : uint32_t
    'I', # inverterWhDrawn : uint32_t
    'I', # inverterWhCharged : uint32_t
    'i', # EcuSetCurrent : int32_t
    'i', # EcuSetCurrentBrake : int32_t
    'B', # pump_duty_cycle : uint8_t
    '1x', # pad 1 bytes before fan_duty_cycle
    'h', # fan_duty_cycle : int16_t
    '?', # active_aero_state : bool
    '1x', # pad 1 bytes before active_aero_position
    'h', # active_aero_position : int16_t
    'B', # accel_lut_id_response : uint8_t
    '?', # reset_gen_efuse : bool
    '?', # reset_ac_efuse : bool
    '?', # igbt_temp_limiting : bool
    '?', # battery_temp_limiting : bool
    '?', # motor_temp_limiting : bool
    'B', # torque_status : uint8_t
    '1x', # pad 1 bytes before flo_temperature_0
    'f', # flo_temperature_0 : float
    'f', # flo_temperature_1 : float
    'f', # flo_temperature_2 : float
    'f', # flo_temperature_3 : float
    'f', # fli_temperature_4 : float
    'f', # fli_temperature_5 : float
    'f', # fli_temperature_6 : float
    'f', # fli_temperature_7 : float
    'f', # fro_temperature_0 : float
    'f', # fro_temperature_1 : float
    'f', # fro_temperature_2 : float
    'f', # fro_temperature_3 : float
    'f', # fri_temperature_4 : float
    'f', # fri_temperature_5 : float
    'f', # fri_temperature_6 : float
    'f', # fri_temperature_7 : float
    'f', # blo_temperature_0 : float
    'f', # blo_temperature_1 : float
    'f', # blo_temperature_2 : float
    'f', # blo_temperature_3 : float
    'f', # bli_temperature_4 : float
    'f', # bli_temperature_5 : float
    'f', # bli_temperature_6 : float
    'f', # bli_temperature_7 : float
    'f', # bro_temperature_0 : float
    'f', # bro_temperature_1 : float
    'f', # bro_temperature_2 : float
    'f', # bro_temperature_3 : float
    'f', # bri_temperature_4 : float
    'f', # bri_temperature_5 : float
    'f', # bri_temperature_6 : float
    'f', # bri_temperature_7 : float
    'f', # fl_speed : float
    'f', # fl_displacement : float
    'f', # fl_load : float
    'f', # fr_speed : float
    'f', # fr_displacement : float
    'f', # fr_load : float
    'f', # bl_speed : float
    'f', # bl_displacement : float
    'f', # bl_load : float
    'f', # br_speed : float
    'f', # br_displacement : float
    'f', # br_load : float
    'B', # file_status : uint8_t
    'B', # num_lut_pairs : uint8_t
    'B', # interp_type : uint8_t
    'B', # lut_id : uint8_t
    'h', # x_zero : int16_t
    '2x', # pad 2 bytes before y_zero
    'f', # y_zero : float
    'h', # x_one : int16_t
    '2x', # pad 2 bytes before y_one
    'f', # y_one : float
    'h', # x_two : int16_t
    '2x', # pad 2 bytes before y_two
    'f', # y_two : float
    'h', # x_three : int16_t
    '2x', # pad 2 bytes before y_three
    'f', # y_three : float
    'h', # x_four : int16_t
    '2x', # pad 2 bytes before y_four
    'f', # y_four : float
    'h', # x_five : int16_t
    '2x', # pad 2 bytes before y_five
    'f', # y_five : float
    'h', # x_six : int16_t
    '2x', # pad 2 bytes before y_six
    'f', # y_six : float
    'h', # x_seven : int16_t
    '2x', # pad 2 bytes before y_seven
    'f', # y_seven : float
    'h', # x_eight : int16_t
    '2x', # pad 2 bytes before y_eight
    'f', # y_eight : float
    'h', # x_nine : int16_t
    '2x', # pad 2 bytes before y_nine
    'f', # y_nine : float
    'h', # x_ten : int16_t
    '2x', # pad 2 bytes before y_ten
    'f', # y_ten : float
    'h', # x_eleven : int16_t
    '2x', # pad 2 bytes before y_eleven
    'f', # y_eleven : float
    'h', # x_twelve : int16_t
    '2x', # pad 2 bytes before y_twelve
    'f', # y_twelve : float
    'h', # x_thirteen : int16_t
    '2x', # pad 2 bytes before y_thirteen
    'f', # y_thirteen : float
    'h', # x_fourteen : int16_t
    '2x', # pad 2 bytes before y_fourteen
    'f', # y_fourteen : float
    'h', # x_fifteen : int16_t
    '2x', # pad 2 bytes before y_fifteen
    'f', # y_fifteen : float
    'h', # x_sixteen : int16_t
    '2x', # pad 2 bytes before y_sixteen
    'f', # y_sixteen : float
    'h', # x_seventeen : int16_t
    '2x', # pad 2 bytes before y_seventeen
    'f', # y_seventeen : float
    'h', # x_eighteen : int16_t
    '2x', # pad 2 bytes before y_eighteen
    'f', # y_eighteen : float
    'h', # x_nineteen : int16_t
    '2x', # pad 2 bytes before y_nineteen
    'f', # y_nineteen : float
    'h', # x_twenty : int16_t
    '2x', # pad 2 bytes before y_twenty
    'f', # y_twenty : float
    'h', # x_twenty_one : int16_t
    '2x', # pad 2 bytes before y_twenty_one
    'f', # y_twenty_one : float
    'h', # x_twenty_two : int16_t
    '2x', # pad 2 bytes before y_twenty_two
    'f', # y_twenty_two : float
    'h', # x_twenty_three : int16_t
    '2x', # pad 2 bytes before y_twenty_three
    'f', # y_twenty_three : float
    'h', # x_twenty_four : int16_t
    '2x', # pad 2 bytes before y_twenty_four
    'f', # y_twenty_four : float
    'h', # x_twenty_five : int16_t
    '2x', # pad 2 bytes before y_twenty_five
    'f', # y_twenty_five : float
    'h', # x_twenty_six : int16_t
    '2x', # pad 2 bytes before y_twenty_six
    'f', # y_twenty_six : float
    'h', # x_twenty_seven : int16_t
    '2x', # pad 2 bytes before y_twenty_seven
    'f', # y_twenty_seven : float
    'h', # x_twenty_eight : int16_t
    '2x', # pad 2 bytes before y_twenty_eight
    'f', # y_twenty_eight : float
    'h', # x_twenty_nine : int16_t
    '2x', # pad 2 bytes before y_twenty_nine
    'f', # y_twenty_nine : float
    'f', # x_acceleration : float
    'f', # y_acceleration : float
    'f', # z_acceleration : float
    'f', # x_angular_speed : float
    'f', # y_angular_speed : float
    'f', # z_angular_speed : float
    'f', # air_speed_0 : float
    'f', # air_speed_1 : float
    'f', # air_speed_2 : float
    'f', # air_speed_3 : float
    'f', # air_speed_4 : float
    'f', # air_speed_5 : float
    'f', # air_speed_6 : float
    'f', # air_speed_7 : float
    'f', # before_motor_flow_rate : float
    'f', # before_accumulator_flow_rate : float
    'f', # before_motor_temperature : float
    'f', # before_accumulator_temperature : float
    'I', # time_since_1970 : uint32_t
    'f', # longitude : float
    'f', # latitude : float
    'B', # wireless_status : uint8_t
    'B', # logger_status : uint8_t
    'B', # ecu_enable_response : uint8_t
    'B', # bms_enable_response : uint8_t
    'B', # pdm_enable_response : uint8_t
    'B', # dynamics_enable_response : uint8_t
    'B', # front_enable_response : uint8_t
    'B', # telemetry_enable_response : uint8_t
    'B', # bl_enable_response : uint8_t
    'B', # br_enable_response : uint8_t
    'B', # fl_enable_response : uint8_t
    'B', # fr_enable_response : uint8_t
    'B', # ecu_status : uint8_t
    'B', # bms_status : uint8_t
    'B', # pdm_status : uint8_t
    'B', # dynamics_status : uint8_t
    'B', # front_status : uint8_t
    'B', # telemetry_status : uint8_t
    'B', # bl_status : uint8_t
    'B', # br_status : uint8_t
    'B', # fl_status : uint8_t
    'B', # fr_status : uint8_t
    '2x', # pad 2 bytes before steering_angle
    'f', # steering_angle : float
    '80f', # cellTemperatures[80] : float
    '140f', # cellVoltages[140] : float
])

validate_size()
