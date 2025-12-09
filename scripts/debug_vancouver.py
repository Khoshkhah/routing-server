
import requests
import json

SERVER_URL = "http://localhost:8000" # Use API Gateway (8000) this time as it's running
# Or 8080 if we want direct server access, but User used API.
# Let's use 8000 to mimic user exactly.
DATASET = "all_vancouver"

def test_routes():
    start = {"lat": 49.12692, "lon": -122.76535}
    end = {"lat": 49.34347, "lon": -123.10387}
    
    print(f"Testing {DATASET} from {start} to {end}")

    # 1. Test One-to-One
    print("\n--- Testing One-to-One ---")
    payload_one = {
        "dataset": DATASET,
        "search_mode": "one_to_one", # API Gateway expects 'search_mode'
        "source_lat": start["lat"],
        "source_lon": start["lon"], 
        "target_lat": end["lat"],
        "target_lon": end["lon"],
        "search_radius": 500.0
    }
    # Note: Gateway uses different param names than direct server (source_lat vs start_lat)
    # Check api/server.py: source_lat, source_lon, target_lat, target_lon
    
    try:
        # Use GET for API Gateway as per logs
        # GET /route?dataset=...
        resp = requests.get(f"{SERVER_URL}/route", params=payload_one, timeout=10)
        res = resp.json()
        print(f"One-to-One Distance: {res.get('distance')}")
        print(f"One-to-One Length: {res.get('distance_meters')}") # Assuming API maps it
    except Exception as e:
        print(f"Error One-to-One: {e}")

    # 2. Test KNN k=1
    print("\n--- Testing KNN k=1 ---")
    payload_knn = {
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
        resp = requests.get(f"{SERVER_URL}/route", params=payload_knn, timeout=10)
        res = resp.json()
        print(f"KNN k=1 Distance: {res.get('distance')}")
        print(f"KNN k=1 Length: {res.get('distance_meters')}")
    except Exception as e:
        print(f"Error KNN: {e}")

if __name__ == "__main__":
    test_routes()
