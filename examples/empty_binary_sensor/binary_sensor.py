import esphome.codegen as cg
from esphome.components import binary_sensor
import esphome.config_validation as cv

empty_binary_sensor_ns = cg.esphome_ns.namespace("empty_binary_sensor")

EmptyBinarySensor = empty_binary_sensor_ns.class_(
    "EmptyBinarySensor", binary_sensor.BinarySensor, cg.Component
)

CONFIG_SCHEMA = binary_sensor.binary_sensor_schema(EmptyBinarySensor).extend(
    cv.COMPONENT_SCHEMA
)


async def to_code(config):
    var = await binary_sensor.new_binary_sensor(config)
    await cg.register_component(var, config)
