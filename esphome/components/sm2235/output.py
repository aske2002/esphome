import esphome.codegen as cg
from esphome.components import output
import esphome.config_validation as cv
from esphome.const import CONF_CHANNEL, CONF_ID

from . import SM2235

DEPENDENCIES = ["sm2235"]
CODEOWNERS = ["@Cossid"]

Channel = SM2235.class_("Channel", output.FloatOutput)

CONF_SM2235_ID = "sm2235_id"
CONFIG_SCHEMA = output.FLOAT_OUTPUT_SCHEMA.extend(
    {
        cv.GenerateID(CONF_SM2235_ID): cv.use_id(SM2235),
        cv.Required(CONF_ID): cv.declare_id(Channel),
        cv.Required(CONF_CHANNEL): cv.int_range(min=0, max=65535),
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await output.register_output(var, config)

    parent = await cg.get_variable(config[CONF_SM2235_ID])
    cg.add(var.set_parent(parent))
    cg.add(var.set_channel(config[CONF_CHANNEL]))
