# Routing Server

A high-performance C++ HTTP server for routing queries using Contraction Hierarchies algorithm.

## Overview

A high-performance C++ routing engine based on Contraction Hierarchies. This server acts as the backend for the routing pipeline, handling shortest path computations efficiently.

> [!NOTE]
> This project is **Stage 4** of the [Routing-Pipeline](https://github.com/khoshkhah/routing-pipeline) ecosystem. It serves the query engine built by [dijkstra-on-Hierarchy](https://github.com/khoshkhah/dijkstra-on-Hierarchy) via a REST API.

## Architecture

The server integrates the **Shortcut Graph** (Contraction Hierarchies) directly into memory. It performs two main steps for each routing request:
1.  **Spatial Search**: Uses a Boost R-tree to find the nearest road network edges to the provided start/end coordinates.
2.  **Shortest Path**: Uses the loaded Contraction Hierarchy to compute the optimal path between these edges.

## Features

- **Persistent Dataset Loading**: Load routing data once at startup instead of per-query
- **REST API**: HTTP endpoints for health checks, dataset loading, and route computation
- **Multi-threading**: Configurable thread pool for concurrent requests
- **Contraction Hierarchies**: Efficient shortest path algorithm with H3 spatial constraints
- **GeoJSON Output**: Route results returned as GeoJSON for easy visualization

## API Endpoints
 
### 1. `GET /health`
Check server status and list loaded datasets.
 
**Response:**
```json
{
  "status": "healthy",
  "datasets_loaded": ["burnaby", "somerset"]
}
```
 
### 2. `POST /load_dataset`
Load a dataset into memory. Idempotent (does nothing if already loaded).
 
**Request:**
```json
{
  "dataset": "burnaby"
}
```
 
**Response:**
```json
{
  "success": true,
  "dataset": "burnaby"
}
```

### 3. `POST /unload_dataset`
Unload a dataset from memory. Idempotent (returns success even if already unloaded).

**Request:**
```json
{
  "dataset": "burnaby"
}
```

**Response:**
```json
{
  "success": true,
  "dataset": "burnaby",
  "was_loaded": true
}
```

### 4. `GET /nearest_edge` or `POST /nearest_edge`
Find the single nearest roadmap edge to a coordinate.
 
**GET Request:** `/nearest_edge?dataset=burnaby&lat=49.25&lon=-123.0`
 
**POST Request:**
```json
{
  "dataset": "burnaby",
  "lat": 49.25,
  "lon": -123.00
}
```

**Response:**
```json
{
  "success": true,
  "edge_id": 12345,
  "distance_meters": 15.4,
  "runtime_ms": 0.1
}
```
 
### 5. `GET /nearest_edges` or `POST /nearest_edges`
Find multiple nearest edges (k-Nearest Neighbors) within a radius.
 
**GET Request:** `/nearest_edges?dataset=burnaby&lat=49.25&lon=-123.0&radius=500&max_candidates=5`
 
**Response:**
```json
{
  "success": true,
  "edges": [
    {"id": 12345, "distance": 15.4},
    {"id": 67890, "distance": 42.1}
  ]
}
```
 
### 6. `POST /route`
Compute shortest path between two coordinates.
 
**Request:**
```json
{
  "dataset": "burnaby",
  "start_lat": 49.123,
  "start_lng": -123.456,
  "end_lat": 49.789,
  "end_lng": -123.012,
  "search_radius": 1000.0,
  "max_candidates": 10
}
```
 
**Response:**
```json
{
  "success": true,
  "route": {
    "distance": 1234.56,
    "distance_meters": 5432.1,
    "runtime_ms": 2.3,
    "path": [1, 2, 3, 4, 5],
    "geojson": {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[-123.456, 49.123], [-123.445, 49.134]]
      },
      "properties": {
          "distance": 1234.56,
          "length_meters": 5432.1
      }
    }
  },
  "timing_breakdown": {
      "find_nearest_us": 12,
      "search_us": 1500,
      "expand_us": 40,
      "geojson_us": 100
  },
  "debug": {
       "cells": {
           "source": {"id": 613699780060643327, "res": 6, "boundary": [[...]]},
           "target": {"id": 613699780024991743, "res": 6, "boundary": [[...]]},
           "high": {"id": 604692580852039679, "res": 6, "boundary": [[...]]}
       }
  }
}
```

> [!TIP]
> **One-to-One Mode**: The routing engine now supports optimal point-to-point queries that utilize the full graph connectivity (including base edges) by relaxing hierarchy constraints for local searches.

## Building

### Prerequisites

- CMake 3.16+
- C++20 compiler
- Boost libraries
- nlohmann/json library
- Crow HTTP framework

### Build Steps

```bash
# Clone and setup dependencies
# (Install Boost, nlohmann/json, Crow via package manager or manually)

# Build the project
./scripts/build.sh

# Run the server
./scripts/run.sh

# Stop the server
./scripts/stop.sh
```

## Configuration

Server configuration is specified in `config/server_config.json`:

```json
{
  "port": 8080,
  "host": "0.0.0.0",
  "thread_count": 4,
  "datasets_path": "../routing-pipeline/data"
}
```

## Dataset Format

Datasets should be organized as follows:

```
data/
├── dataset_name/
│   ├── shortcuts.parquet    # Contraction Hierarchies shortcuts
│   ├── edges.csv           # Edge metadata (id, geometry, length, highway)
│   └── spatial_index/      # Spatial indexing files (optional)
```

## Performance

- **Dataset Loading**: ~30-60 seconds for large datasets (done once at startup)
- **Query Response**: < 10ms for typical routing queries
- **Memory Usage**: ~2-4GB per large dataset
- **Concurrent Requests**: Scales with thread count configuration

## Integration

This server replaces the subprocess-based approach in the routing-pipeline. Update your client code to use HTTP POST requests instead of subprocess calls.

Example migration from Python:

```python
# Old approach (subprocess)
result = subprocess.run([binary_path, ...], capture_output=True)

# New approach (HTTP)
response = requests.post("http://localhost:8080/route", json=payload)
route = response.json()["route"]
```