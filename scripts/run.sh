#!/bin/bash

# Run script for routing-server

set -e

echo "Starting routing-server..."

# Check if binary exists
if [ ! -f "build/routing-server" ]; then
    echo "Binary not found. Please run build.sh first."
    exit 1
fi

# Run the server
./build/routing-server config/server_config.json