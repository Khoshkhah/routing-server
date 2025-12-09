
import requests
import json

SERVER_URL = "http://localhost:8080"
DATASET = "burnaby"

def test_routes():
    # Use coordinates that are likely to find a road
    # Example coordinates (Burnaby-ish)
    start = {"lat": 49.2827, "lon": -122.9781}
    end = {"lat": 49.2500, "lon": -122.9500}
    
    # 1. Test One-to-One
    print("\n--- Testing One-to-One ---")
    payload_one = {
        "dataset": DATASET,
        "start_lat": start["lat"],
        "start_lng": start["lon"],
        "end_lat": end["lat"],
        "end_lng": end["lon"],
        "mode": "one_to_one",
        "search_radius": 1000.0
    }
    try:
        resp = requests.post(f"{SERVER_URL}/route", json=payload_one, timeout=5)
        res = resp.json()
        print(f"One-to-One Result: {json.dumps(res, indent=2)}")
        return # Stop here to avoid buffer truncation
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test KNN k=1
    print("\n--- Testing KNN k=1 ---")
    payload_knn = {
        "dataset": DATASET,
        "start_lat": start["lat"],
        "start_lng": start["lon"],
        "end_lat": end["lat"],
        "end_lng": end["lon"],
        "mode": "knn",
        "max_candidates": 1,
        "search_radius": 1000.0
    }
    try:
        resp = requests.post(f"{SERVER_URL}/route", json=payload_knn, timeout=5)
        res = resp.json()
        print(f"KNN k=1 Distance: {res.get('route', {}).get('distance')}")
        print(f"KNN k=1 Path Len: {len(res.get('route', {}).get('path', []))}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_routes()
