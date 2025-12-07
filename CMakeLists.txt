cmake_minimum_required(VERSION 3.16)
project(routing-server VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find dependencies
# Crow and nlohmann/json are header-only libraries included via include_directories
find_package(Boost REQUIRED COMPONENTS system filesystem)
find_package(GTest REQUIRED)
find_package(Arrow REQUIRED CONFIG)
find_package(Parquet REQUIRED CONFIG)

find_path(H3_INCLUDE_DIR h3api.h PATH_SUFFIXES h3)
find_library(H3_LIBRARY h3)
if (NOT H3_INCLUDE_DIR OR NOT H3_LIBRARY)
    message(FATAL_ERROR "H3 headers or library not found.")
endif()

# Include directories
include_directories(include)
include_directories(${CMAKE_SOURCE_DIR}/../dijkstra-on-Hierarchy/cpp/include)
include_directories(${CMAKE_SOURCE_DIR}/third_party/crow/include)
include_directories(${CMAKE_SOURCE_DIR}/third_party/json/include)
include_directories(${H3_INCLUDE_DIR})

# Source files
set(SOURCES
    src/main.cpp
    src/server.cpp
    src/routing_engine.cpp
    ${CMAKE_SOURCE_DIR}/../dijkstra-on-Hierarchy/cpp/src/shortcut_graph.cpp
    ${CMAKE_SOURCE_DIR}/../dijkstra-on-Hierarchy/cpp/src/h3_utils.cpp
)

set(ARROW_TARGET Arrow::arrow_shared)
if (NOT TARGET ${ARROW_TARGET})
    set(ARROW_TARGET Arrow::arrow)
endif()

set(PARQUET_TARGET Parquet::parquet_shared)
if (NOT TARGET ${PARQUET_TARGET})
    set(PARQUET_TARGET Parquet::parquet)
endif()

add_executable(routing-server ${SOURCES})
target_link_libraries(routing-server
    Boost::system
    Boost::filesystem
    ${ARROW_TARGET}
    ${PARQUET_TARGET}
    ${H3_LIBRARY}
)

# Test executable
set(TEST_SOURCES
    tests/test_routing_engine.cpp
    src/routing_engine.cpp
    ${CMAKE_SOURCE_DIR}/../dijkstra-on-Hierarchy/cpp/src/shortcut_graph.cpp
    ${CMAKE_SOURCE_DIR}/../dijkstra-on-Hierarchy/cpp/src/h3_utils.cpp
)

add_executable(routing-server-test ${TEST_SOURCES})
target_link_libraries(routing-server-test
    GTest::gtest_main
    Boost::system
    Boost::filesystem
    ${ARROW_TARGET}
    ${PARQUET_TARGET}
    ${H3_LIBRARY}
)

# Enable testing
enable_testing()
add_test(NAME routing-engine-test COMMAND routing-server-test)