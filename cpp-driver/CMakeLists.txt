cmake_minimum_required(VERSION 3.10)
project(InstrumentDriver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(instrument_driver
    main.cpp
    instrument_driver.cpp
)

# Build instructions:
#   mkdir build && cd build
#   cmake ..
#   cmake --build .
#   echo "*IDN?" | ./instrument_driver
