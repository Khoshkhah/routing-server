import requests
import json

SERVER_URL = "http://localhost:8080"
DATASET = "somerset"

# Test: Compare query() vs query_multi_optimized() for SAME single source/target
SOURCE_EDGE = 748
TARGET_EDGE = 2899

print("Testing direct C++ backend comparison:")
print(f"Source Edge: {SOURCE_EDGE}")
print(f"Target Edge: {TARGET_EDGE}")
print()

# Load dataset
payload = {
    "dataset": DATASET,
    "shortcuts_path": "../spark-shortest-path/output/Somerset_shortcuts_final",
    "edges_path": "../spark-shortest-path/data/Somerset_driving_simplified_edges_with_h3.csv"
}
requests.post(f"{SERVER_URL}/load_dataset", json=payload, timeout=60)

# Test 1: Single source/target using query_multi_optimized (simulating n=1)
print("=" * 80)
print("Test 1: query_multi_optimized with single source/target")
print("=" * 80)
payload1 = {
    "dataset": DATASET,
    "start_lat": 37.08702,
    "start_lng": -84.57730,
    "end_lat": 37.10202,
    "end_lng": -84.61807,
    "mode": "knn",
    "num_candidates": 1,
    "search_radius": 500.0
}
resp1 = requests.post(f"{SERVER_URL}/route", json=payload1, timeout=10)
result1 = resp1.json()
if result1.get("success"):
    route1 = result1.get("route", {})
    print(f"Cost: {route1.get('distance')}")
    print(f"Path length: {len(route1.get('path', []))}")
    print(f"Path: {route1.get('path')[:10]}...")  # First 10 edges
else:
    print(f"Failed: {result1.get('error')}")

print()

# Test 2: Multiple sources/targets using query_multi_optimized (simulating n=2)
print("=" * 80)
print("Test 2: query_multi_optimized with multiple sources/targets")
print("=" * 80)
payload2 = {
    "dataset": DATASET,
    "start_lat": 37.08702,
    "start_lng": -84.57730,
    "end_lat": 37.10202,
    "end_lng": -84.61807,
    "mode": "knn",
    "num_candidates": 2,
    "search_radius": 500.0
}
resp2 = requests.post(f"{SERVER_URL}/route", json=payload2, timeout=10)
result2 = resp2.json()
if result2.get("success"):
    route2 = result2.get("route", {})
    print(f"Cost: {route2.get('distance')}")
    print(f"Path length: {len(route2.get('path', []))}")
    print(f"Path: {route2.get('path')[:10]}...")  # First 10 edges
else:
    print(f"Failed: {result2.get('error')}")

print()
print("=" * 80)
print("ANALYSIS")
print("=" * 80)
if result1.get("success") and result2.get("success"):
    cost1 = result1["route"]["distance"]
    cost2 = result2["route"]["distance"]
    if abs(cost1 - cost2) < 0.01:
        print("✅ PASS: Costs are identical")
    else:
        print(f"❌ FAIL: Cost difference = {abs(cost1 - cost2):.2f}s")
        print(f"  n=1: {cost1:.2f}s")
        print(f"  n=2: {cost2:.2f}s")
