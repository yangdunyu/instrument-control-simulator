#pragma once
#include <string>

/**
 * Lightweight C++ instrument driver mock.
 *
 * Implements a subset of SCPI-like commands to demonstrate
 * that the same command protocol can be driven from native code.
 * Compiled as a standalone CLI: pipe commands via stdin/stdout.
 */
class InstrumentDriver {
public:
    std::string handleCommand(const std::string& command);

private:
    double      powerDbm_      = 0.0;
    bool        outputEnabled_ = false;
    std::string firmwareVer_   = "1.0.0";
};
