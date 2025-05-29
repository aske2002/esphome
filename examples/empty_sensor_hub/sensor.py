import esphome.codegen as cg
from esphome.components import sensor
import esphome.config_validation as cv
from esphome.const import ICON_EMPTY, UNIT_EMPTY

from . import CONF_EMPTY_SENSOR_HUB_ID, HUB_CHILD_SCHEMA

DEPENDENCIES = ["empty_sensor_hub"]

CONFIG_SCHEMA = (
    sensor.sensor_schema(
        unit_of_measurement=UNIT_EMPTY, icon=ICON_EMPTY, accuracy_decimals=1
    )
    .extend(HUB_CHILD_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA)
)


async def to_code(config):
    paren = await cg.get_variable(config[CONF_EMPTY_SENSOR_HUB_ID])
    var = await sensor.new_sensor(config)

    cg.add(paren.register_sensor(var))
