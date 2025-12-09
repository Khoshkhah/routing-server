#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:8080"
source = {"lat": 37.07422, "lon": -84.62563}
target = {"lat": 37.09709, "lon": -84.59541}

# Load dataset
requests.post(f"{BASE_URL}/load-dataset", json={"dataset": "somerset"})

# One-to-One
r1 = requests.get(f"{BASE_URL}/route", params={
    "dataset": "somerset",
    "search_mode": "one_to_one",
    "source_lat": source["lat"],
    "source_lon": source["lon"],
    "target_lat": target["lat"],
    "target_lon": target["lon"],
    "search_radius": 500.0
})
d1 = r1.json()

# KNN n=1
r2 = requests.get(f"{BASE_URL}/route", params={
    "dataset": "somerset",
    "search_mode": "knn",
    "num_candidates": 1,
    "source_lat": source["lat"],
    "source_lon": source["lon"],
    "target_lat": target["lat"],
    "target_lon": target["lon"],
    "search_radius": 500.0
})
d2 = r2.json()

print("="*80)
print("COMPARISON")
print("="*80)
print(f"One-to-One Cost: {d1.get('distance', 'N/A')}")
print(f"KNN n=1 Cost:    {d2.get('distance', 'N/A')}")
if d1.get('distance') and d2.get('distance'):
    print(f"Difference:      {abs(d1['distance'] - d2['distance']):.4f}s")
    if abs(d1['distance'] - d2['distance']) < 0.01:
        print("\n✅ Costs match!")
    else:
        print("\n⚠️  Costs differ!")
