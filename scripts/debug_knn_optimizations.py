import requests
import json
import time

SERVER_URL = "http://localhost:8000"
DATASET = "somerset"

# Case 1: Source == Target
# Edge 2556
LAT_START = 37.08065
LON_START = -84.59880

# Case 2: Direct Shortcut
# 2558 -> 2559
start_direct = {'lat': 37.08411, 'lon': -84.60148}
end_direct = {'lat': 37.08187, 'lon': -84.60036}

def test_knn_optimizations():
    print(f"Loading {DATASET}...")
    try:
        requests.post(f"{SERVER_URL}/load-dataset", json={"dataset": DATASET})
    except:
        pass
    time.sleep(1)

    # 1. Test Source == Target in KNN n=2
    print("\n--- Testing Case 1: Source == Target (KNN n=2) ---")
    payload_1 = {
        "dataset": DATASET,
        "search_mode": "knn",
        "num_candidates": 2, # Forces Optimized Mode
        "source_lat": LAT_START,
        "source_lon": LON_START,
        "target_lat": LAT_START,
        "target_lon": LON_START,
        "search_radius": 500.0
    }
    try:
        resp = requests.get(f"{SERVER_URL}/route", params=payload_1, timeout=5)
        res = resp.json()
        print(f"KNN n=2 Source=Target Result: Distance={res.get('distance')}")
        # print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"Error Case 1: {e}")

    # 2. Test Direct Shortcut in KNN n=2
    print("\n--- Testing Case 2: Direct Shortcut (KNN n=2) ---")
    payload_2 = {
        "dataset": DATASET,
        "search_mode": "knn",
        "num_candidates": 2, # Forces Optimized Mode
        "source_lat": start_direct["lat"],
        "source_lon": start_direct["lon"],
        "target_lat": end_direct["lat"],
        "target_lon": end_direct["lon"],
        "search_radius": 500.0
    }
    try:
        resp = requests.get(f"{SERVER_URL}/route", params=payload_2, timeout=5)
        res = resp.json()
        print(f"KNN n=2 Direct Shortcut Result: Distance={res.get('distance')}")
        # print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"Error Case 2: {e}")

if __name__ == "__main__":
    test_knn_optimizations()
