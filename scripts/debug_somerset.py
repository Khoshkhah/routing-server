import requests
import json

SERVER_URL = "http://localhost:8000"
DATASET = "somerset"

# User coordinates
start = {"lat": 37.08411, "lon": -84.60148}
end = {"lat": 37.08187, "lon": -84.60036}

def test_somerset():
    print(f"Testing {DATASET} from {start} to {end}")
    
    for n in [1, 2, 3]:
        print(f"\n--- Testing KNN n={n} ---")
        payload = {
            "dataset": DATASET,
            "search_mode": "knn",
            "num_candidates": n,
            "source_lat": start["lat"],
            "source_lon": start["lon"],
            "target_lat": end["lat"],
            "target_lon": end["lon"],
            "search_radius": 500.0
        }
        try:
            resp = requests.get(f"{SERVER_URL}/route", params=payload, timeout=10)
            res = resp.json()
            print(f"Full Response n={n}: {json.dumps(res, indent=2)}")
            print(f"KNN n={n} Cost (Time): {res.get('distance')}")
            print(f"KNN n={n} Length (Meters): {res.get('distance_meters')}")
        except Exception as e:
            print(f"Error KNN n={n}: {e}")

if __name__ == "__main__":
    test_somerset()
