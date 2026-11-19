cmake_minimum_required(VERSION 3.15)
project(RDR2_MCP_Bridge LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_definitions(-D_CRT_SECURE_NO_WARNINGS -DWIN32_LEAN_AND_MEAN)

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

set(SOURCES
    src/main.cpp
)

add_library(${PROJECT_NAME} SHARED ${SOURCES})

# Target output as .asi
set_target_properties(${PROJECT_NAME} PROPERTIES
    SUFFIX ".asi"
    PREFIX ""
    OUTPUT_NAME "RDR2_MCP_Bridge"
)

target_link_libraries(${PROJECT_NAME}
    ws2_32
    user32
)
