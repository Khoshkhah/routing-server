#!/bin/bash
pkill -f routing-server || true
sleep 1
nohup ./build/routing-server config/server_config.json > server.log 2>&1 &
echo "Server restarted. PID: $!"
