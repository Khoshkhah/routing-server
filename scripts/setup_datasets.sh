#!/bin/bash
set -e

# Define paths
ROUTING_PIPELINE_DATA="/home/kaveh/projects/routing-pipeline/data"
SPARK_OUTPUT="/home/kaveh/projects/spark-shortest-path/output"
OSM_OUTPUT="/home/kaveh/projects/osm-to-road-network/data/output"

# Create directories
mkdir -p "$ROUTING_PIPELINE_DATA/burnaby"
mkdir -p "$ROUTING_PIPELINE_DATA/somerset"

# Link Burnaby
echo "Linking Burnaby..."
ln -sf "$SPARK_OUTPUT/Burnaby_shortcuts_final" "$ROUTING_PIPELINE_DATA/burnaby/shortcuts.parquet"
ln -sf "$OSM_OUTPUT/Burnaby_driving_simplified_edges_with_h3.csv" "$ROUTING_PIPELINE_DATA/burnaby/edges.csv"

# Link Somerset
echo "Linking Somerset..."
if [ -d "$SPARK_OUTPUT/Somerset_shortcuts_final" ]; then
    ln -sf "$SPARK_OUTPUT/Somerset_shortcuts_final" "$ROUTING_PIPELINE_DATA/somerset/shortcuts.parquet"
    ln -sf "$OSM_OUTPUT/Somerset_driving_simplified_edges_with_h3.csv" "$ROUTING_PIPELINE_DATA/somerset/edges.csv"
else
    echo "Warning: Somerset shortcuts not found in spark output."
fi

echo "Datasets setup complete."
ls -R "$ROUTING_PIPELINE_DATA"
