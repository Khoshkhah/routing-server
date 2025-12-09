#!/usr/bin/env python3
"""
Test script for the specific Somerset route with coordinates:
source = 37.07956, -84.62185 target = 37.10612, -84.61464
Testing KNN n=1 and one-to-one mode
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8080"

# Test route coordinates
source = {"lat": 37.07956, "lon": -84.62185}
target = {"lat": 37.10612, "lon": -84.61464}
dataset = "somerset"

print("="*80)
print("Testing Somerset Route")
print("="*80)
print(f"Source: ({source['lat']}, {source['lon']})")
print(f"Target: ({target['lat']}, {target['lon']})")
print()

# Load dataset
print("Loading dataset...")
try:
    load_response = requests.post(f"{BASE_URL}/load_dataset", json={"dataset": dataset}, timeout=5)
    load_data = load_response.json()
    print(f"Load response: {load_data}")
except Exception as e:
    print(f"Error loading dataset: {e}")
print()

# Test one-to-one mode
print("="*80)
print("ONE-TO-ONE MODE")
print("="*80)
one_to_one_params = {
    "dataset": dataset,
    "mode": "one_to_one",
    "start_lat": source["lat"],
    "start_lng": source["lon"],
    "end_lat": target["lat"],
    "end_lng": target["lon"],
    "search_radius": 500.0,
    "max_candidates": 1
}
one_to_one_data = None
try:
    one_to_one_response = requests.post(f"{BASE_URL}/route", json=one_to_one_params, timeout=10)
    one_to_one_data = one_to_one_response.json()
    
    print(json.dumps(one_to_one_data, indent=2))
    
    if one_to_one_data.get("success"):
        route = one_to_one_data["route"]
        print(f"\nCost (Time): {route.get('distance', 'N/A')} seconds")
        print(f"Distance (Meters): {route.get('distance_meters', 'N/A')} m")
        print(f"Path Length: {len(route.get('path', []))} edges")
    else:
        print(f"\nError: {one_to_one_data.get('error')}")
except Exception as e:
    print(f"Error in one-to-one mode: {e}")
print()

# Test KNN n=1 mode
print("="*80)
print("KNN n=1 MODE")
print("="*80)
knn_params = {
    "dataset": dataset,
    "mode": "knn",
    "num_candidates": 1,
    "start_lat": source["lat"],
    "start_lng": source["lon"],
    "end_lat": target["lat"],
    "end_lng": target["lon"],
    "search_radius": 500.0,
    "max_candidates": 1
}
knn_data = None
try:
    knn_response = requests.post(f"{BASE_URL}/route", json=knn_params, timeout=10)
    knn_data = knn_response.json()
    
    print(json.dumps(knn_data, indent=2))
    
    if knn_data.get("success"):
        route = knn_data["route"]
        print(f"\nCost (Time): {route.get('distance', 'N/A')} seconds")
        print(f"Distance (Meters): {route.get('distance_meters', 'N/A')} m")
        print(f"Path Length: {len(route.get('path', []))} edges")
    else:
        print(f"\nError: {knn_data.get('error')}")
except Exception as e:
    print(f"Error in KNN mode: {e}")
print()

# Compare results
print("="*80)
print("COMPARISON")
print("="*80)
if one_to_one_data and knn_data and one_to_one_data.get("success") and knn_data.get("success"):
    one_to_one_cost = one_to_one_data["route"].get("distance")
    knn_cost = knn_data["route"].get("distance")
    one_to_one_dist = one_to_one_data["route"].get("distance_meters")
    knn_dist = knn_data["route"].get("distance_meters")
    
    if one_to_one_cost and knn_cost:
        diff = abs(one_to_one_cost - knn_cost)
        print(f"One-to-One Cost: {one_to_one_cost:.4f}s")
        print(f"KNN n=1 Cost: {knn_cost:.4f}s")
        print(f"Cost Difference: {diff:.4f}s ({abs(one_to_one_cost - knn_cost) / one_to_one_cost * 100:.2f}%)")
    
    if one_to_one_dist and knn_dist:
        dist_diff = abs(one_to_one_dist - knn_dist)
        print(f"\nOne-to-One Distance: {one_to_one_dist:.2f}m")
        print(f"KNN n=1 Distance: {knn_dist:.2f}m")
        print(f"Distance Difference: {dist_diff:.2f}m ({abs(one_to_one_dist - knn_dist) / one_to_one_dist * 100:.2f}%)")
elif one_to_one_data and knn_data:
    print("One or both modes failed - check error messages above")
else:
    print("No responses received from one or both modes")
