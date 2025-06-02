#include "uart_controller.h"
#include "esphome/core/log.h"

namespace esphome {
namespace uart_controller {
static const char *TAG = "uart_controller";

void UartController::setup() {
  this->join_pin_->setup();  // Make sure it's an output
  this->transmit_enable_pin_->setup();
  this->tx_data_pin_->setup();
  this->rx_pin_->setup();  // Assuming this is a GPIOPin* as input

  // Step 1: Start JOIN process
  this->join_pin_->digital_write(true);  // short Ta/Tb
  this->state_ = ControllerState::JOINING;
  this->join_start_time_ = millis();
}

void UartController::update() {}

void UartController::dump_config() { ESP_LOGCONFIG(TAG, "UartController:"); }

void UartController::loop() {
  switch (this->state_) {
    case JOINING:
      // Ensure we've waited at least 1–2 seconds before checking Rx
      if (this->rx_pin_->digital_read()) {
        this->join_pin_->digital_write(false);  // release short
        ESP_LOGE(TAG, "Join process completed, waiting for Rx to go high.");
      };
      break;

    case WAITING_FOR_RX_HIGH:
      if (this->rx_pin_->digital_read()) {
        this->transmit_enable_pin_->digital_write(true);
        this->state_ = READY_TO_TRANSMIT;
      }
      break;

    case READY_TO_TRANSMIT:
      ESP_LOGV(TAG, "Ready to transmit. Waiting for Tx data.");
      break;

    case TRANSMITTING:
      ESP_LOGV(TAG, "Transmitting data...");
      break;
    default:
      ESP_LOGW(TAG, "Unknown state: %d", this->state_);
      break;
  }

  // Handle incoming byte from UART, if applicable
  if (available() > 0) {
    uint8_t incomingByte;
    this->read_byte(&incomingByte);
    char cmdByte = (char) incomingByte;
    for (auto &it : sensorset_) {
      it->parse_input(cmdByte);
    }
  }
}

void UartController::dump_sensors_() {
  ESP_LOGV(TAG, "sensors");
  for (auto &it : sensorset_) {
    ESP_LOGV(TAG, "  Sensor 0x%x", it);
    it->dump_config();
  }
}
}  // namespace uart_controller

}  // namespace esphome
