#include <cstdint>

struct DriveBusData {
    bool bmsFaults[8];
    bool ecuFaults[5];

    float hvVoltage;
    float lvVoltage;
    float batteryTemp;
    float maxCellTemp;
    float minCellTemp;
    float maxCellVoltage;
    float minCellVoltage;
    float maxDischargeCurrent;
    float maxRegenCurrent;
    float bmsSOC;

    float wheelSpeeds[4];
    float wheelDisplacement[4];
    float prStrain[4];
    float genAmps;
    float fanAmps;
    float pumpAmps;

    uint16_t bmsFaultsRaw;
    int16_t motorRPM;
    int16_t motorCurrent;
    int16_t motorDCVoltage;
    int16_t motorDCCurrent;
    int16_t frontBrakePressure;
    int16_t rearBreakPressure;
    int16_t apps1;
    int16_t apps2;
    uint16_t inverterIGBTTemp;
    uint16_t inverterMotorTemp;

    uint8_t driveState;
    uint8_t bmsState;
    uint8_t imdState = 1;  // healthy when high
    uint8_t inverterStatus;
    uint8_t bmsCommand;

    bool brakePressed;
    bool lvVoltageWarning;

    bool pdmGenEfuseTriggered;
    bool pdmACEfuseTriggered;

    uint32_t inverterAhDrawn;
    uint32_t inverterAhCharged;

    uint32_t inverterWhDrawn;
    uint32_t inverterWhCharged;

    int32_t EcuSetCurrent;
    int32_t EcuSetCurrentBrake;

    uint8_t pump_duty_cycle;
    int16_t fan_duty_cycle;

    bool active_aero_state;
    int16_t active_aero_position;

    uint8_t accel_lut_id_response;

    bool reset_gen_efuse;
    bool reset_ac_efuse;

    bool igbt_temp_limiting;
    bool battery_temp_limiting;
    bool motor_temp_limiting;

    uint8_t torque_status;

    float flo_temperature_0;
    float flo_temperature_1;
    float flo_temperature_2;
    float flo_temperature_3;

    float fli_temperature_4;
    float fli_temperature_5;
    float fli_temperature_6;
    float fli_temperature_7;

    float fro_temperature_0;
    float fro_temperature_1;
    float fro_temperature_2;
    float fro_temperature_3;

    float fri_temperature_4;
    float fri_temperature_5;
    float fri_temperature_6;
    float fri_temperature_7;

    float blo_temperature_0;
    float blo_temperature_1;
    float blo_temperature_2;
    float blo_temperature_3;

    float bli_temperature_4;
    float bli_temperature_5;
    float bli_temperature_6;
    float bli_temperature_7;

    float bro_temperature_0;
    float bro_temperature_1;
    float bro_temperature_2;
    float bro_temperature_3;

    float bri_temperature_4;
    float bri_temperature_5;
    float bri_temperature_6;
    float bri_temperature_7;

    float fl_speed;
    float fl_displacement;
    float fl_load;

    float fr_speed;
    float fr_displacement;
    float fr_load;

    float bl_speed;
    float bl_displacement;
    float bl_load;

    float br_speed;
    float br_displacement;
    float br_load;

    uint8_t file_status;
    uint8_t num_lut_pairs;
    uint8_t interp_type;
    uint8_t lut_id;

    int16_t x_zero;
    float y_zero;
    int16_t x_one;
    float y_one;

    int16_t x_two;
    float y_two;
    int16_t x_three;
    float y_three;

    int16_t x_four;
    float y_four;
    int16_t x_five;
    float y_five;

    int16_t x_six;
    float y_six;
    int16_t x_seven;
    float y_seven;

    int16_t x_eight;
    float y_eight;
    int16_t x_nine;
    float y_nine;

    int16_t x_ten;
    float y_ten;
    int16_t x_eleven;
    float y_eleven;

    int16_t x_twelve;
    float y_twelve;
    int16_t x_thirteen;
    float y_thirteen;

    int16_t x_fourteen;
    float y_fourteen;
    int16_t x_fifteen;
    float y_fifteen;

    int16_t x_sixteen;
    float y_sixteen;
    int16_t x_seventeen;
    float y_seventeen;

    int16_t x_eighteen;
    float y_eighteen;
    int16_t x_nineteen;
    float y_nineteen;

    int16_t x_twenty;
    float y_twenty;
    int16_t x_twenty_one;
    float y_twenty_one;

    int16_t x_twenty_two;
    float y_twenty_two;
    int16_t x_twenty_three;
    float y_twenty_three;

    int16_t x_twenty_four;
    float y_twenty_four;
    int16_t x_twenty_five;
    float y_twenty_five;

    int16_t x_twenty_six;
    float y_twenty_six;
    int16_t x_twenty_seven;
    float y_twenty_seven;

    int16_t x_twenty_eight;
    float y_twenty_eight;
    int16_t x_twenty_nine;
    float y_twenty_nine;

    float x_acceleration;
    float y_acceleration;
    float z_acceleration;

    float x_angular_speed;
    float y_angular_speed;
    float z_angular_speed;

    float air_speed_0;
    float air_speed_1;
    float air_speed_2;
    float air_speed_3;

    float air_speed_4;
    float air_speed_5;
    float air_speed_6;
    float air_speed_7;

    float before_motor_flow_rate;
    float before_accumulator_flow_rate;

    float before_motor_temperature;
    float before_accumulator_temperature;

    uint32_t time_since_1970;
    float longitude;
    float latitude;
    uint8_t wireless_status;
    uint8_t logger_status;

    uint8_t ecu_enable_response;
    uint8_t bms_enable_response;
    uint8_t pdm_enable_response;

    uint8_t dynamics_enable_response;
    uint8_t front_enable_response;
    uint8_t telemetry_enable_response;

    uint8_t bl_enable_response;
    uint8_t br_enable_response;
    uint8_t fl_enable_response;
    uint8_t fr_enable_response;

    uint8_t ecu_status;
    uint8_t bms_status;
    uint8_t pdm_status;

    uint8_t dynamics_status;
    uint8_t front_status;
    uint8_t telemetry_status;

    uint8_t bl_status;
    uint8_t br_status;
    uint8_t fl_status;
    uint8_t fr_status;

    float steering_angle;

    float cellTemperatures[80];
    float cellVoltages[140];
};