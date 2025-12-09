import requests
import json
import time

SERVER_URL = "http://localhost:8000"
DATASET = "somerset"

# Test Case 1: A -> B
LAT_A = 37.08269
LON_A = -84.60829
LAT_B = 37.08766
LON_B = -84.60629

def test_route(source_lat, source_lon, target_lat, target_lon, label):
    print(f"\n{'='*80}")
    print(f"{label}")
    print(f"Source: ({source_lat}, {source_lon}) -> Target: ({target_lat}, {target_lon})")
    print(f"{'='*80}")
    
    for n in [1, 2]:
        print(f"\n--- KNN n={n} ---")
        payload = {
            "dataset": DATASET,
            "search_mode": "knn",
            "num_candidates": n,
            "source_lat": source_lat,
            "source_lon": source_lon,
            "target_lat": target_lat,
            "target_lon": target_lon,
            "search_radius": 500.0
        }
        try:
            resp = requests.get(f"{SERVER_URL}/route", params=payload, timeout=5)
            res = resp.json()
            if res.get("success"):
                print(f"Cost (Time): {res.get('distance'):.4f}s")
                path = res.get('path')
                print(f"Extended Path: {path}")
                if path and len(path) > 0:
                    print(f"Selected Source Edge: {path[0]}")
                    print(f"Selected Target Edge: {path[-1]}")
                
                debug_info = res.get("debug")
                if debug_info:
                    src_cands = debug_info.get('source_candidates', [])
                    tgt_cands = debug_info.get('target_candidates', [])
                    print(f"\nSource Candidates ({len(src_cands)}): {[c['edge_id'] for c in src_cands]}")
                    print(f"Target Candidates ({len(tgt_cands)}): {[c['edge_id'] for c in tgt_cands]}")
            else:
                print(f"Failed: {res.get('error')}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Loading {DATASET}...")
    try:
        requests.post(f"{SERVER_URL}/load-dataset", json={"dataset": DATASET})
    except:
        pass
    time.sleep(1)
    
    # Test A -> B
    test_route(LAT_A, LON_A, LAT_B, LON_B, "TEST CASE 1: A -> B")
    
    # Test B -> A
    test_route(LAT_B, LON_B, LAT_A, LON_A, "TEST CASE 2: B -> A (Reverse)")
