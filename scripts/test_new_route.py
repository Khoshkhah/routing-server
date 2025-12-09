#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:8000"
source = {"lat": 37.07956, "lon": -84.62185}
target = {"lat": 37.10612, "lon": -84.61464}

# Load dataset
print("Loading dataset...")
r = requests.post(f"{BASE_URL}/load-dataset", json={"dataset": "somerset"})
print(r.json())
print()

# One-to-One
print("="*80)
print("ONE-TO-ONE MODE")
print("="*80)
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
print(f"Cost: {d1.get('distance', 'N/A')}")
if 'debug' in d1 and d1['debug']:
    print(f"Source: edge {d1['debug']['source_candidates'][0]['edge_id']}")
    print(f"Target: edge {d1['debug']['target_candidates'][0]['edge_id']}")
if 'path' in d1 and d1['path']:
    print(f"Path Length: {len(d1['path'])} edges")
print()

# KNN n=1
print("="*80)
print("KNN n=1 MODE")
print("="*80)
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
print(f"Cost: {d2.get('distance', 'N/A')}")
if 'debug' in d2 and d2['debug']:
    print(f"Source: edge {d2['debug']['source_candidates'][0]['edge_id']}")
    print(f"Target: edge {d2['debug']['target_candidates'][0]['edge_id']}")
if 'path' in d2 and d2['path']:
    print(f"Path Length: {len(d2['path'])} edges")
print()

# Comparison
print("="*80)
print("COMPARISON")
print("="*80)
if d1.get('distance') and d2.get('distance'):
    print(f"One-to-One: {d1['distance']:.4f}s")
    print(f"KNN n=1:    {d2['distance']:.4f}s")
    diff = abs(d1['distance'] - d2['distance'])
    print(f"Difference: {diff:.4f}s")
    
    if diff < 0.01:
        print("\n✅ Costs MATCH!")
    else:
        print(f"\n⚠️  Costs DIFFER by {diff:.2f}s!")
        if d1['distance'] > d2['distance']:
            print("   One-to-one found a LONGER path (hierarchical filtering issue)")
        else:
            print("   KNN found a LONGER path (unexpected!)")
else:
    print("Error: Could not compare - one or both queries failed")
    print(f"One-to-One: {d1.get('error', 'No error')}")
    print(f"KNN n=1: {d2.get('error', 'No error')}")
