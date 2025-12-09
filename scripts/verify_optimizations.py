import requests
import json
import time

SERVER_URL = "http://localhost:8000"
DATASET = "somerset"

# Known coordinates from debugging
LAT_START = 37.08065
LON_START = -84.59880
LAT_END = 37.10051
LON_END = -84.61593

def test_optimizations():
    print(f"Loading {DATASET}...")
    requests.post(f"{SERVER_URL}/load-dataset", json={"dataset": DATASET})
    time.sleep(1)

    # 1. Test Source == Target (Optimization 1)
    print("\n--- Testing Case 1: Source == Target ---")
    payload_1 = {
        "dataset": DATASET,
        "search_mode": "one_to_one",
        "source_lat": LAT_START,
        "source_lon": LON_START,
        "target_lat": LAT_START, # Same as source
        "target_lon": LON_START,
        "search_radius": 500.0
    }
    try:
        resp = requests.get(f"{SERVER_URL}/route", params=payload_1, timeout=5)
        res = resp.json()
        print(f"Case 1 Result: {json.dumps(res, indent=2)}")
    except Exception as e:
        print(f"Error Case 1: {e}")

    # 2. Test Direct Shortcut (Optimization 2)
    # Using the coordinates that produced path [2744, 2559] in KNN mode
    # Start: {'lat': 37.08411, 'lon': -84.60148}
    # End: {'lat': 37.08187, 'lon': -84.60036}
    print("\n--- Testing Case 2: Direct Shortcut Candidate ---")
    start_direct = {'lat': 37.08411, 'lon': -84.60148}
    end_direct = {'lat': 37.08187, 'lon': -84.60036}
    
    payload_2 = {
        "dataset": DATASET,
        "search_mode": "one_to_one",
        "source_lat": start_direct["lat"],
        "source_lon": start_direct["lon"],
        "target_lat": end_direct["lat"],
        "target_lon": end_direct["lon"],
        "search_radius": 500.0
    }
    try:
        resp = requests.get(f"{SERVER_URL}/route", params=payload_2, timeout=5)
        res = resp.json()
        print(f"Case 2 Result: {json.dumps(res, indent=2)}")
    except Exception as e:
        print(f"Error Case 2: {e}")

if __name__ == "__main__":
    test_optimizations()
