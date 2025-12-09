#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:8000"
source = {"lat": 37.07422, "lon": -84.62563}
target = {"lat": 37.09709, "lon": -84.59541}

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
print(f"One-to-One Cost: {d1['distance']:.4f}s")
print(f"KNN n=1 Cost:    {d2['distance']:.4f}s")
print(f"Difference:      {abs(d1['distance'] - d2['distance']):.4f}s")
print()

if 'debug' in d1:
    print("One-to-One Debug:")
    print(f"  Source: edge {d1['debug']['source_candidates'][0]['edge_id']}")
    print(f"  Target: edge {d1['debug']['target_candidates'][0]['edge_id']}")
print()

if 'debug' in d2:
    print("KNN n=1 Debug:")
    print(f"  Source: edge {d2['debug']['source_candidates'][0]['edge_id']}")
    print(f"  Target: edge {d2['debug']['target_candidates'][0]['edge_id']}")
print()

print(f"One-to-One Path Length: {len(d1.get('path', []))} edges")
print(f"KNN n=1 Path Length:    {len(d2.get('path', []))} edges")
