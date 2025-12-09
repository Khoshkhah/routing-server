import requests
import json

SERVER_URL = "http://localhost:8000"
DATASET = "somerset"

# User coordinates Case 2
start = {"lat": 37.08065, "lon": -84.59880}
end = {"lat": 37.10051, "lon": -84.61593}

def test_somerset_case2():
    print(f"Testing {DATASET} from {start} to {end}")
    
    for n in [1, 2]:
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
            # print(f"Full Response n={n}: {json.dumps(res, indent=2)}")
            print(f"KNN n={n} Cost (Time): {res.get('distance')}")
            print(f"KNN n={n} Length (Meters): {res.get('distance_meters')}")
            print(f"KNN n={n} Path: {res.get('path')}")
            
        except Exception as e:
            print(f"Error KNN n={n}: {e}")

if __name__ == "__main__":
    test_somerset_case2()
