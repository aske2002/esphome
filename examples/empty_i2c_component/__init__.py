import esphome.codegen as cg
from esphome.components import i2c
import esphome.config_validation as cv
from esphome.const import CONF_ID

DEPENDENCIES = ["i2c"]

empty_i2c_component_ns = cg.esphome_ns.namespace("empty_i2c_component")
EmptyI2CComponent = empty_i2c_component_ns.class_(
    "EmptyI2CComponent", cg.Component, i2c.I2CDevice
)

CONFIG_SCHEMA = (
    cv.Schema({cv.GenerateID(): cv.declare_id(EmptyI2CComponent)})
    .extend(cv.COMPONENT_SCHEMA)
    .extend(i2c.i2c_device_schema(0x01))
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)
