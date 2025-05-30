import esphome.codegen as cg
from esphome.components.binary_sensor import BinarySensor
from esphome.components.rotary_encoder.sensor import RotaryEncoderSensor
import esphome.config_validation as cv
from esphome.const import CONF_GROUP, CONF_ID, CONF_SENSOR

from .defines import (
    CONF_DEFAULT_GROUP,
    CONF_ENCODERS,
    CONF_ENTER_BUTTON,
    CONF_INITIAL_FOCUS,
    CONF_LEFT_BUTTON,
    CONF_LONG_PRESS_REPEAT_TIME,
    CONF_LONG_PRESS_TIME,
    CONF_RIGHT_BUTTON,
)
from .helpers import lvgl_components_required, requires_component
from .lvcode import lv, lv_add, lv_assign, lv_expr, lv_Pvariable
from .schemas import ENCODER_SCHEMA
from .types import lv_group_t, lv_indev_type_t, lv_key_t
from .widgets import get_widgets

ENCODERS_CONFIG = cv.ensure_list(
    ENCODER_SCHEMA.extend(
        {
            cv.Required(CONF_ENTER_BUTTON): cv.use_id(BinarySensor),
            cv.Required(CONF_SENSOR): cv.Any(
                cv.All(
                    cv.use_id(RotaryEncoderSensor), requires_component("rotary_encoder")
                ),
                cv.Schema(
                    {
                        cv.Required(CONF_LEFT_BUTTON): cv.use_id(BinarySensor),
                        cv.Required(CONF_RIGHT_BUTTON): cv.use_id(BinarySensor),
                    }
                ),
            ),
        }
    )
)


def get_default_group(config):
    default_group = cg.Pvariable(config[CONF_DEFAULT_GROUP], lv_expr.group_create())
    cg.add(lv.group_set_default(default_group))
    return default_group


async def encoders_to_code(var, config, default_group):
    for enc_conf in config[CONF_ENCODERS]:
        lvgl_components_required.add("KEY_LISTENER")
        lpt = enc_conf[CONF_LONG_PRESS_TIME].total_milliseconds
        lprt = enc_conf[CONF_LONG_PRESS_REPEAT_TIME].total_milliseconds
        listener = cg.new_Pvariable(
            enc_conf[CONF_ID], lv_indev_type_t.LV_INDEV_TYPE_ENCODER, lpt, lprt
        )
        await cg.register_parented(listener, var)
        if sensor_config := enc_conf.get(CONF_SENSOR):
            if isinstance(sensor_config, dict):
                b_sensor = await cg.get_variable(sensor_config[CONF_LEFT_BUTTON])
                cg.add(listener.add_button(b_sensor, lv_key_t.LV_KEY_LEFT))
                b_sensor = await cg.get_variable(sensor_config[CONF_RIGHT_BUTTON])
                cg.add(listener.add_button(b_sensor, lv_key_t.LV_KEY_RIGHT))
            else:
                sensor_config = await cg.get_variable(sensor_config)
                lv_add(listener.set_sensor(sensor_config))
        b_sensor = await cg.get_variable(enc_conf[CONF_ENTER_BUTTON])
        cg.add(listener.add_button(b_sensor, lv_key_t.LV_KEY_ENTER))
        if group := enc_conf.get(CONF_GROUP):
            group = lv_Pvariable(lv_group_t, group)
            lv_assign(group, lv_expr.group_create())
        else:
            group = default_group
        lv.indev_set_group(lv_expr.indev_drv_register(listener.get_drv()), group)


async def initial_focus_to_code(config):
    for enc_conf in config[CONF_ENCODERS]:
        if default_focus := enc_conf.get(CONF_INITIAL_FOCUS):
            widget = await get_widgets(default_focus)
            lv.group_focus_obj(widget[0].obj)
