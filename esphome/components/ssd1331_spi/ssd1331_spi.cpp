#include "ssd1331_spi.h"
#include "esphome/core/log.h"
#include "esphome/core/application.h"

namespace esphome {
namespace ssd1331_spi {

static const char *const TAG = "ssd1331_spi";

void SPISSD1331::setup() {
  ESP_LOGCONFIG(TAG, "Running setup");
  this->spi_setup();
  this->dc_pin_->setup();  // OUTPUT
  if (this->cs_)
    this->cs_->setup();  // OUTPUT

  this->init_reset_();
  delay(500);  // NOLINT
  SSD1331::setup();
}
void SPISSD1331::dump_config() {
  LOG_DISPLAY("", "SPI SSD1331", this);
  LOG_PIN("  CS Pin: ", this->cs_);
  LOG_PIN("  DC Pin: ", this->dc_pin_);
  LOG_PIN("  Reset Pin: ", this->reset_pin_);
  ESP_LOGCONFIG(TAG, "  Initial Brightness: %.2f", this->brightness_);
  LOG_UPDATE_INTERVAL(this);
}
void SPISSD1331::command(uint8_t value) {
  if (this->cs_)
    this->cs_->digital_write(true);
  this->dc_pin_->digital_write(false);
  delay(1);
  this->enable();
  if (this->cs_)
    this->cs_->digital_write(false);
  this->write_byte(value);
  if (this->cs_)
    this->cs_->digital_write(true);
  this->disable();
}
void HOT SPISSD1331::write_display_data() {
  if (this->cs_)
    this->cs_->digital_write(true);
  this->dc_pin_->digital_write(true);
  if (this->cs_)
    this->cs_->digital_write(false);
  delay(1);
  this->enable();
  this->write_array(this->buffer_, this->get_buffer_length_());
  if (this->cs_)
    this->cs_->digital_write(true);
  this->disable();
}

}  // namespace ssd1331_spi
}  // namespace esphome
