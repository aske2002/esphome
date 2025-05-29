import esphome.codegen as cg
from esphome.components import binary_sensor
import esphome.config_validation as cv

from . import CONF_EMPTY_SENSOR_HUB_ID, HUB_CHILD_SCHEMA

DEPENDENCIES = ["empty_sensor_hub"]

CONFIG_SCHEMA = (
    binary_sensor.binary_sensor_schema()
    .extend(HUB_CHILD_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA)
)


async def to_code(config):
    paren = await cg.get_variable(config[CONF_EMPTY_SENSOR_HUB_ID])
    var = await binary_sensor.new_binary_sensor(config)

    cg.add(paren.register_binary_sensor(var))
