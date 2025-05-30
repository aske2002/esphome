
#include "modbus_switch.h"
#include "esphome/core/log.h"
namespace esphome {
namespace modbus_controller {

static const char *const TAG = "modbus_controller.switch";

void ModbusSwitch::setup() {
  optional<bool> initial_state = Switch::get_initial_state_with_restore_mode();
  if (initial_state.has_value()) {
    // if it has a value, restore_mode is not "DISABLED", therefore act on the switch:
    if (initial_state.value()) {
      this->turn_on();
    } else {
      this->turn_off();
    }
  }
}
void ModbusSwitch::dump_config() { LOG_SWITCH(TAG, "Modbus Controller Switch", this); }

void ModbusSwitch::set_assumed_state(bool assumed_state) { this->assumed_state_ = assumed_state; }

bool ModbusSwitch::assumed_state() { return this->assumed_state_; }

void ModbusSwitch::parse_and_publish(const std::vector<uint8_t> &data) {
  bool value = false;
  switch (this->register_type) {
    case ModbusRegisterType::DISCRETE_INPUT:
    case ModbusRegisterType::COIL:
      // offset for coil is the actual number of the coil not the byte offset
      value = coil_from_vector(this->offset, data);
      break;
    default:
      value = get_data<uint16_t>(data, this->offset) & this->bitmask;
      break;
  }

  // Is there a lambda registered
  // call it with the pre converted value and the raw data array
  if (this->publish_transform_func_) {
    // the lambda can parse the response itself
    auto val = (*this->publish_transform_func_)(this, value, data);
    if (val.has_value()) {
      ESP_LOGV(TAG, "Value overwritten by lambda");
      value = val.value();
    }
  }

  ESP_LOGV(TAG, "Publish '%s': new value = %s type = %d address = %X offset = %x", this->get_name().c_str(),
           ONOFF(value), (int) this->register_type, this->start_address, this->offset);
  this->publish_state(value);
}

void ModbusSwitch::write_state(bool state) {
  // This will be called every time the user requests a state change.
  ModbusCommandItem cmd;
  std::vector<uint8_t> data;
  // Is there are lambda configured?
  if (this->write_transform_func_.has_value()) {
    // data is passed by reference
    // the lambda can fill the empty vector directly
    // in that case the return value is ignored
    auto val = (*this->write_transform_func_)(this, state, data);
    if (val.has_value()) {
      ESP_LOGV(TAG, "Value overwritten by lambda");
      state = val.value();
    } else {
      ESP_LOGV(TAG, "Communication handled by lambda - exiting control");
      return;
    }
  }
  if (!data.empty()) {
    ESP_LOGV(TAG, "Modbus Switch write raw: %s", format_hex_pretty(data).c_str());
    cmd = ModbusCommandItem::create_custom_command(
        this->parent_, data,
        [this, cmd](ModbusRegisterType register_type, uint16_t start_address, const std::vector<uint8_t> &data) {
          this->parent_->on_write_register_response(cmd.register_type, this->start_address, data);
        });
  } else {
    ESP_LOGV(TAG, "write_state '%s': new value = %s type = %d address = %X offset = %x", this->get_name().c_str(),
             ONOFF(state), (int) this->register_type, this->start_address, this->offset);
    if (this->register_type == ModbusRegisterType::COIL) {
      // offset for coil and discrete inputs is the coil/register number not bytes
      if (this->use_write_multiple_) {
        std::vector<bool> states{state};
        cmd = ModbusCommandItem::create_write_multiple_coils(this->parent_, this->start_address + this->offset, states);
      } else {
        cmd = ModbusCommandItem::create_write_single_coil(this->parent_, this->start_address + this->offset, state);
      }
    } else {
      // since offset is in bytes and a register is 16 bits we get the start by adding offset/2
      if (this->use_write_multiple_) {
        std::vector<uint16_t> bool_states(1, state ? (0xFFFF & this->bitmask) : 0);
        cmd = ModbusCommandItem::create_write_multiple_command(this->parent_, this->start_address + this->offset / 2, 1,
                                                               bool_states);
      } else {
        cmd = ModbusCommandItem::create_write_single_command(this->parent_, this->start_address + this->offset / 2,
                                                             state ? 0xFFFF & this->bitmask : 0u);
      }
    }
  }
  this->parent_->queue_command(cmd);
  this->publish_state(state);
}
// ModbusSwitch end
}  // namespace modbus_controller
}  // namespace esphome
