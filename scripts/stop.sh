#!/bin/bash
# Stop the routing-server process

echo "Stopping routing-server..."
pkill -f "routing-server"

if [ $? -eq 0 ]; then
    echo "Routing server stopped successfully."
else
    echo "No running routing-server found or failed to stop."
fi
