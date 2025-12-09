import requests
import json
import time

SERVER_URL = "http://localhost:8000"
DATASET = "somerset"

# Case 4 (User Request)
LAT_START = 37.07964
LON_START = -84.60610
LAT_END = 37.08275
LON_END = -84.60293

def test_somerset_case3():
    print(f"Loading {DATASET}...")
    try:
        requests.post(f"{SERVER_URL}/load-dataset", json={"dataset": DATASET})
    except:
        pass
    time.sleep(1)

    print(f"Testing Somerset Case 3: {LAT_START},{LON_START} -> {LAT_END},{LON_END}")

    for n in [1, 2]:
        print(f"\n--- Testing KNN n={n} ---")
        payload = {
            "dataset": DATASET,
            "search_mode": "knn",
            "num_candidates": n,
            "source_lat": LAT_START,
            "source_lon": LON_START,
            "target_lat": LAT_END,
            "target_lon": LON_END,
            "search_radius": 500.0
        }
        try:
            resp = requests.get(f"{SERVER_URL}/route", params=payload, timeout=5)
            res = resp.json()
            if res.get("success"):
                print(f"KNN n={n} Cost (Time): {res.get('distance')}")
                path = res.get('path')
                print(f"KNN n={n} Extended Path: {path}")
                if path and len(path) > 0:
                    print(f"KNN n={n} Selected Source Edge: {path[0]}")
                    print(f"KNN n={n} Selected Target Edge: {path[-1]}")
                
                # Print Full Candidate List
                # print(f"Response Keys: {list(res.keys())}")
                debug_info = res.get("debug")
                print(f"Debug Info Raw: {debug_info}") 
                
                if debug_info:
                    print(f"KNN n={n} Source Candidates: {json.dumps(debug_info.get('source_candidates'), indent=2)}")
                    print(f"KNN n={n} Target Candidates: {json.dumps(debug_info.get('target_candidates'), indent=2)}")
                else:
                    print("Debug field is falsy (None or Empty)")
            else:
                print(f"KNN n={n} Failed: {res.get('error')}")
        except Exception as e:
            print(f"Error KNN n={n}: {e}")

if __name__ == "__main__":
    test_somerset_case3()
