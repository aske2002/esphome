#include "hdc1080.h"
#include "esphome/core/log.h"
#include "esphome/core/hal.h"

namespace esphome {
namespace hdc1080 {

static const char *const TAG = "hdc1080";

static const uint8_t HDC1080_ADDRESS = 0x40;  // 0b1000000 from datasheet
static const uint8_t HDC1080_CMD_CONFIGURATION = 0x02;
static const uint8_t HDC1080_CMD_TEMPERATURE = 0x00;
static const uint8_t HDC1080_CMD_HUMIDITY = 0x01;

void HDC1080Component::setup() {
  ESP_LOGCONFIG(TAG, "Running setup");

  const uint8_t data[2] = {
      0b00000000,  // resolution 14bit for both humidity and temperature
      0b00000000   // reserved
  };

  if (!this->write_bytes(HDC1080_CMD_CONFIGURATION, data, 2)) {
    // as instruction is same as powerup defaults (for now), interpret as warning if this fails
    ESP_LOGW(TAG, "HDC1080 initial config instruction error");
    this->status_set_warning();
    return;
  }
}
void HDC1080Component::dump_config() {
  ESP_LOGCONFIG(TAG, "HDC1080:");
  LOG_I2C_DEVICE(this);
  if (this->is_failed()) {
    ESP_LOGE(TAG, ESP_LOG_MSG_COMM_FAIL);
  }
  LOG_UPDATE_INTERVAL(this);
  LOG_SENSOR("  ", "Temperature", this->temperature_);
  LOG_SENSOR("  ", "Humidity", this->humidity_);
}
void HDC1080Component::update() {
  uint16_t raw_temp;
  if (this->write(&HDC1080_CMD_TEMPERATURE, 1) != i2c::ERROR_OK) {
    this->status_set_warning();
    return;
  }
  delay(20);
  if (this->read(reinterpret_cast<uint8_t *>(&raw_temp), 2) != i2c::ERROR_OK) {
    this->status_set_warning();
    return;
  }
  raw_temp = i2c::i2ctohs(raw_temp);
  float temp = raw_temp * 0.0025177f - 40.0f;  // raw * 2^-16 * 165 - 40
  this->temperature_->publish_state(temp);

  uint16_t raw_humidity;
  if (this->write(&HDC1080_CMD_HUMIDITY, 1) != i2c::ERROR_OK) {
    this->status_set_warning();
    return;
  }
  delay(20);
  if (this->read(reinterpret_cast<uint8_t *>(&raw_humidity), 2) != i2c::ERROR_OK) {
    this->status_set_warning();
    return;
  }
  raw_humidity = i2c::i2ctohs(raw_humidity);
  float humidity = raw_humidity * 0.001525879f;  // raw * 2^-16 * 100
  this->humidity_->publish_state(humidity);

  ESP_LOGD(TAG, "Got temperature=%.1f°C humidity=%.1f%%", temp, humidity);
  this->status_clear_warning();
}
float HDC1080Component::get_setup_priority() const { return setup_priority::DATA; }

}  // namespace hdc1080
}  // namespace esphome
