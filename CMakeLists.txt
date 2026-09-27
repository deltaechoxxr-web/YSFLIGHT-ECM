cmake_minimum_required(VERSION 3.16)
project(ysflight_ecm_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(ysflight_ecm_demo
    src/main.cpp
    src/ecm.cpp
)

target_include_directories(ysflight_ecm_demo
    PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src
)
