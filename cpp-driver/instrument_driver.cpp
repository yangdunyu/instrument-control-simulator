#include "instrument_driver.h"

#include <sstream>
#include <stdexcept>

std::string InstrumentDriver::handleCommand(const std::string& command) {
    if (command == "*IDN?") {
        return "Quantifi-Sim,CPP-DRIVER,SIM-001," + firmwareVer_;
    }

    if (command == "SYST:VERS?") {
        return firmwareVer_;
    }

    if (command == "OUTP ON") {
        outputEnabled_ = true;
        return "OK";
    }

    if (command == "OUTP OFF") {
        outputEnabled_ = false;
        return "OK";
    }

    if (command == "OUTP?") {
        return outputEnabled_ ? "1" : "0";
    }

    if (command == "SOUR:POW?") {
        std::ostringstream oss;
        oss << powerDbm_;
        return oss.str();
    }

    // SOUR:POW <value>
    if (command.rfind("SOUR:POW ", 0) == 0) {
        try {
            double val = std::stod(command.substr(9));
            if (val < -60.0 || val > 10.0) return "ERROR:POWER_OUT_OF_RANGE";
            powerDbm_ = val;
            return "OK";
        } catch (...) {
            return "ERROR:INVALID_PARAM";
        }
    }

    return "ERROR:UNKNOWN_COMMAND";
}
