import requests
import json

SERVER_URL = "http://localhost:8000"
DATASET = "all_vancouver"

# User coordinates
start = {"lat": 49.33497, "lon": -123.05099}
end = {"lat": 49.11928, "lon": -122.79007}

def test_knn_mismatch():
    print(f"Testing {DATASET} from {start} to {end}")
    
    # 1. KNN n=1 (Strict)
    print("\n--- Testing KNN n=1 (Strict) ---")
    payload_n1 = {
        "dataset": DATASET,
        "search_mode": "knn",
        "num_candidates": 1,
        "source_lat": start["lat"],
        "source_lon": start["lon"],
        "target_lat": end["lat"],
        "target_lon": end["lon"],
        "search_radius": 500.0
    }
    try:
        resp = requests.get(f"{SERVER_URL}/route", params=payload_n1, timeout=10)
        res = resp.json()
        print(f"KNN n=1 Distance: {res.get('distance')}")
        print(f"KNN n=1 Length: {res.get('distance_meters')}")
    except Exception as e:
        print(f"Error KNN n=1: {e}")

    # 2. KNN n=2 (Optimized)
    print("\n--- Testing KNN n=2 (Optimized) ---")
    payload_n2 = {
        "dataset": DATASET,
        "search_mode": "knn",
        "num_candidates": 2,
        "source_lat": start["lat"],
        "source_lon": start["lon"],
        "target_lat": end["lat"],
        "target_lon": end["lon"],
        "search_radius": 500.0
    }
    try:
        resp = requests.get(f"{SERVER_URL}/route", params=payload_n2, timeout=10)
        res = resp.json()
        print(f"KNN n=2 Distance: {res.get('distance')}")
        print(f"KNN n=2 Length: {res.get('distance_meters')}")
    except Exception as e:
        print(f"Error KNN n=2: {e}")
        
    # 3. One-to-One (Strict)
    print("\n--- Testing One-to-One (Strict) ---")
    payload_oto = {
        "dataset": DATASET,
        "search_mode": "one_to_one",
        "source_lat": start["lat"],
        "source_lon": start["lon"],
        "target_lat": end["lat"],
        "target_lon": end["lon"],
        "search_radius": 500.0
    }
    try:
        resp = requests.get(f"{SERVER_URL}/route", params=payload_oto, timeout=10)
        res = resp.json()
        print(f"One-to-One Distance: {res.get('distance')}")
    except Exception as e:
        print(f"Error One-to-One: {e}")

if __name__ == "__main__":
    test_knn_mismatch()
