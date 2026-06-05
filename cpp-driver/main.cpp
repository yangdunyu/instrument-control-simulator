#include <iostream>
#include <string>

#include "instrument_driver.h"

int main() {
    InstrumentDriver driver;
    std::string line;

    std::cout << "Instrument Driver CLI  (Ctrl+D to exit)\n"
              << "Commands: *IDN? SYST:VERS? OUTP ON/OFF OUTP? SOUR:POW <val> SOUR:POW?\n"
              << std::string(60, '-') << "\n";

    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        std::cout << driver.handleCommand(line) << "\n";
    }

    return 0;
}
