import esphome.codegen as cg
from esphome.components import sensor, uart
import esphome.config_validation as cv
from esphome.const import (
    CONF_ADDRESS,
    CONF_CURRENT,
    CONF_ENERGY,
    CONF_FREQUENCY,
    CONF_ID,
    CONF_LINE_FREQUENCY,
    CONF_POWER,
    CONF_RESET,
    CONF_VOLTAGE,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_FREQUENCY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_VOLTAGE,
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    UNIT_AMPERE,
    UNIT_HERTZ,
    UNIT_KILOWATT_HOURS,
    UNIT_VOLT,
    UNIT_WATT,
)

CONF_CURRENT_REFERENCE = "current_reference"
CONF_ENERGY_REFERENCE = "energy_reference"
CONF_POWER_REFERENCE = "power_reference"
CONF_VOLTAGE_REFERENCE = "voltage_reference"

DEPENDENCIES = ["uart"]

bl0942_ns = cg.esphome_ns.namespace("bl0942")
BL0942 = bl0942_ns.class_("BL0942", cg.PollingComponent, uart.UARTDevice)

LineFrequency = bl0942_ns.enum("LineFrequency")
LINE_FREQS = {
    50: LineFrequency.LINE_FREQUENCY_50HZ,
    60: LineFrequency.LINE_FREQUENCY_60HZ,
}

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(BL0942),
            cv.Optional(CONF_VOLTAGE): sensor.sensor_schema(
                unit_of_measurement=UNIT_VOLT,
                accuracy_decimals=1,
                device_class=DEVICE_CLASS_VOLTAGE,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            cv.Optional(CONF_CURRENT): sensor.sensor_schema(
                unit_of_measurement=UNIT_AMPERE,
                accuracy_decimals=2,
                device_class=DEVICE_CLASS_CURRENT,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            cv.Optional(CONF_POWER): sensor.sensor_schema(
                unit_of_measurement=UNIT_WATT,
                accuracy_decimals=1,
                device_class=DEVICE_CLASS_POWER,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            cv.Optional(CONF_ENERGY): sensor.sensor_schema(
                unit_of_measurement=UNIT_KILOWATT_HOURS,
                accuracy_decimals=3,
                device_class=DEVICE_CLASS_ENERGY,
                state_class=STATE_CLASS_TOTAL_INCREASING,
            ),
            cv.Optional(CONF_FREQUENCY): sensor.sensor_schema(
                unit_of_measurement=UNIT_HERTZ,
                accuracy_decimals=2,
                device_class=DEVICE_CLASS_FREQUENCY,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            cv.Optional(CONF_LINE_FREQUENCY, default="50HZ"): cv.All(
                cv.frequency,
                cv.enum(
                    LINE_FREQS,
                    int=True,
                ),
            ),
            cv.Optional(CONF_ADDRESS, default=0): cv.int_range(min=0, max=3),
            cv.Optional(CONF_RESET, default=True): cv.boolean,
            cv.Optional(CONF_CURRENT_REFERENCE): cv.float_,
            cv.Optional(CONF_ENERGY_REFERENCE): cv.float_,
            cv.Optional(CONF_POWER_REFERENCE): cv.float_,
            cv.Optional(CONF_VOLTAGE_REFERENCE): cv.float_,
        }
    )
    .extend(cv.polling_component_schema("60s"))
    .extend(uart.UART_DEVICE_SCHEMA)
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    if voltage_config := config.get(CONF_VOLTAGE):
        sens = await sensor.new_sensor(voltage_config)
        cg.add(var.set_voltage_sensor(sens))
    if current_config := config.get(CONF_CURRENT):
        sens = await sensor.new_sensor(current_config)
        cg.add(var.set_current_sensor(sens))
    if power_config := config.get(CONF_POWER):
        sens = await sensor.new_sensor(power_config)
        cg.add(var.set_power_sensor(sens))
    if energy_config := config.get(CONF_ENERGY):
        sens = await sensor.new_sensor(energy_config)
        cg.add(var.set_energy_sensor(sens))
    if frequency_config := config.get(CONF_FREQUENCY):
        sens = await sensor.new_sensor(frequency_config)
        cg.add(var.set_frequency_sensor(sens))
    cg.add(var.set_line_freq(config[CONF_LINE_FREQUENCY]))
    cg.add(var.set_address(config[CONF_ADDRESS]))
    cg.add(var.set_reset(config[CONF_RESET]))
    if (current_reference := config.get(CONF_CURRENT_REFERENCE, None)) is not None:
        cg.add(var.set_current_reference(current_reference))
    if (voltage_reference := config.get(CONF_VOLTAGE_REFERENCE, None)) is not None:
        cg.add(var.set_voltage_reference(voltage_reference))
    if (power_reference := config.get(CONF_POWER_REFERENCE, None)) is not None:
        cg.add(var.set_power_reference(power_reference))
    if (energy_reference := config.get(CONF_ENERGY_REFERENCE, None)) is not None:
        cg.add(var.set_energy_reference(energy_reference))
