#!/usr/bin/env python3
"""
Test script to compare KNN n=1 vs one-to-one for a specific Somerset route.
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

# Test route
source = {"lat": 37.07422, "lon": -84.62563}
target = {"lat": 37.09709, "lon": -84.59541}
dataset = "somerset"

print("Testing Somerset Route:")
print(f"Source: ({source['lat']}, {source['lon']})")
print(f"Target: ({target['lat']}, {target['lon']})")
print()

# Load dataset
print("Loading dataset...")
load_response = requests.post(f"{BASE_URL}/load-dataset", json={"dataset": dataset})
print(load_response.json())
print()

# Test one-to-one mode
print("="*80)
print("ONE-TO-ONE MODE")
print("="*80)
one_to_one_params = {
    "dataset": dataset,
    "search_mode": "one_to_one",
    "source_lat": source["lat"],
    "source_lon": source["lon"],
    "target_lat": target["lat"],
    "target_lon": target["lon"],
    "search_radius": 500.0
}
one_to_one_response = requests.get(f"{BASE_URL}/route", params=one_to_one_params)
one_to_one_data = one_to_one_response.json()

if one_to_one_data.get("success"):
    route = one_to_one_data["route"]
    print(f"Cost (Time): {route['cost']:.4f}s")
    print(f"Distance (Meters): {route['distance']:.2f}m")
    print(f"Path Length: {len(route.get('path', []))} edges")
else:
    print(f"Error: {one_to_one_data.get('error')}")
print()

# Test KNN n=1 mode
print("="*80)
print("KNN n=1 MODE")
print("="*80)
knn_params = {
    "dataset": dataset,
    "search_mode": "knn",
    "num_candidates": 1,
    "source_lat": source["lat"],
    "source_lon": source["lon"],
    "target_lat": target["lat"],
    "target_lon": target["lon"],
    "search_radius": 500.0
}
knn_response = requests.get(f"{BASE_URL}/route", params=knn_params)
knn_data = knn_response.json()

if knn_data.get("success"):
    route = knn_data["route"]
    print(f"Cost (Time): {route['cost']:.4f}s")
    print(f"Distance (Meters): {route['distance']:.2f}m")
    print(f"Path Length: {len(route.get('path', []))} edges")
    
    # Show debug info if available
    if "debug" in route:
        debug = route["debug"]
        if "source_candidates" in debug:
            print(f"\nSource Candidates ({len(debug['source_candidates'])}):")
            for cand in debug['source_candidates']:
                print(f"  Edge {cand['edge']}: {cand['distance']:.2f}m")
        if "target_candidates" in debug:
            print(f"\nTarget Candidates ({len(debug['target_candidates'])}):")
            for cand in debug['target_candidates']:
                print(f"  Edge {cand['edge']}: {cand['distance']:.2f}m")
else:
    print(f"Error: {knn_data.get('error')}")
print()

# Compare results
print("="*80)
print("COMPARISON")
print("="*80)
if one_to_one_data.get("success") and knn_data.get("success"):
    one_to_one_cost = one_to_one_data["route"]["cost"]
    knn_cost = knn_data["route"]["cost"]
    diff = abs(one_to_one_cost - knn_cost)
    
    print(f"One-to-One Cost: {one_to_one_cost:.4f}s")
    print(f"KNN n=1 Cost:    {knn_cost:.4f}s")
    print(f"Difference:      {diff:.4f}s")
    
    if diff > 0.01:  # Allow small floating point differences
        print("\n⚠️  WARNING: Costs differ! This indicates a bug.")
    else:
        print("\n✅ Costs match!")
