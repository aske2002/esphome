#include "esphome/core/defines.h"
#if defined(USE_RP2040) && defined(USE_MDNS)

#include "esphome/components/network/ip_address.h"
#include "esphome/components/network/util.h"
#include "esphome/core/log.h"
#include "mdns_component.h"

#include <ESP8266mDNS.h>

namespace esphome {
namespace mdns {

void MDNSComponent::setup() {
  this->compile_records_();

  MDNS.begin(this->hostname_.c_str());

  for (const auto &service : this->services_) {
    // Strip the leading underscore from the proto and service_type. While it is
    // part of the wire protocol to have an underscore, and for example ESP-IDF
    // expects the underscore to be there, the ESP8266 implementation always adds
    // the underscore itself.
    auto *proto = service.proto.c_str();
    while (*proto == '_') {
      proto++;
    }
    auto *service_type = service.service_type.c_str();
    while (*service_type == '_') {
      service_type++;
    }
    uint16_t port = const_cast<TemplatableValue<uint16_t> &>(service.port).value();
    MDNS.addService(service_type, proto, port);
    for (const auto &record : service.txt_records) {
      MDNS.addServiceTxt(service_type, proto, record.key.c_str(),
                         const_cast<TemplatableValue<std::string> &>(record.value).value().c_str());
    }
  }
}

void MDNSComponent::loop() { MDNS.update(); }

void MDNSComponent::on_shutdown() {
  MDNS.close();
  delay(40);
}

}  // namespace mdns
}  // namespace esphome

#endif
