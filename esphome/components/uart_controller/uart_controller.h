#pragma once

#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/core/automation.h"
#include "esphome/core/gpio.h"

#include <set>

namespace esphome
{
  namespace uart_controller
  {

    enum ControllerState
    {
      IDLE,
      JOINING,
      WAITING_FOR_RX_HIGH,
      READY_TO_TRANSMIT,
      TRANSMITTING
    };

    class UartController;

    class SensorItem
    {
    public:
      virtual void parse_input(char data) = 0;
      virtual void dump_config() = 0;
    };

    using SensorSet = std::set<SensorItem *>;

    class UartController : public PollingComponent, public uart::UARTDevice
    {
    public:
      void setup() override;
      void loop() override;
      void update() override;
      void dump_config() override;

      void add_sensor_item(SensorItem *item) { sensorset_.insert(item); }

      void set_join_pin(GPIOPin *pin) { join_pin_ = pin; }
      void set_transmit_enable_pin(GPIOPin *pin) { transmit_enable_pin_ = pin; }
      void set_tx_data_pin(GPIOPin *pin) { tx_data_pin_ = pin; }
      void set_rx_pin(GPIOPin *pin) { rx_pin_ = pin; }

    protected:
      void dump_sensors_();

      ControllerState state_ = IDLE;
      uint32_t join_start_time_ = 0;

      GPIOPin *join_pin_;
      GPIOPin *transmit_enable_pin_;
      GPIOPin *tx_data_pin_;
      GPIOPin *rx_pin_;

      SensorSet sensorset_;
    };

  } // namespace uart_controller
} // namespace esphome
