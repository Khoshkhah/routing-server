#!/bin/bash

# Build script for routing-server

set -e

echo "Building routing-server..."

# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake -DCMAKE_BUILD_TYPE=Release ..

# Build
make -j$(nproc)

echo "Build complete. Binary located at: build/routing-server"