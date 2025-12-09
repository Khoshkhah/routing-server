import requests
import json
import time

SERVER_URL = "http://localhost:8000"
DATASET = "somerset"

# Test coordinates
SOURCE_LAT = 37.08586
SOURCE_LON = -84.60232
TARGET_LAT = 37.08000
TARGET_LON = -84.60000

def test_route(search_mode, num_candidates=None):
    print(f"\n{'='*80}")
    if search_mode == "one_to_one":
        print(f"MODE: One-to-One")
    else:
        print(f"MODE: KNN n={num_candidates}")
    print(f"{'='*80}")
    
    payload = {
        "dataset": DATASET,
        "search_mode": search_mode,
        "source_lat": SOURCE_LAT,
        "source_lon": SOURCE_LON,
        "target_lat": TARGET_LAT,
        "target_lon": TARGET_LON,
        "search_radius": 500.0
    }
    
    if search_mode == "knn":
        payload["num_candidates"] = num_candidates
    
    try:
        resp = requests.get(f"{SERVER_URL}/route", params=payload, timeout=5)
        res = resp.json()
        if res.get("success"):
            print(f"Cost (Time): {res.get('distance'):.4f}s")
            print(f"Distance (Meters): {res.get('distance_meters'):.2f}m")
            path = res.get('path')
            print(f"Extended Path: {path}")
            if path and len(path) > 0:
                print(f"Path Length: {len(path)} edges")
                print(f"Selected Source Edge: {path[0]}")
                print(f"Selected Target Edge: {path[-1]}")
            
            debug_info = res.get("debug")
            if debug_info:
                src_cands = debug_info.get('source_candidates', [])
                tgt_cands = debug_info.get('target_candidates', [])
                print(f"\nSource Candidates ({len(src_cands)}):")
                for c in src_cands:
                    print(f"  Edge {c['edge_id']}: {c['dist_m']:.2f}m ({c['dist_s']:.2f}s)")
                print(f"Target Candidates ({len(tgt_cands)}):")
                for c in tgt_cands:
                    print(f"  Edge {c['edge_id']}: {c['dist_m']:.2f}m ({c['dist_s']:.2f}s)")
        else:
            print(f"Failed: {res.get('error')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Testing Somerset Route:")
    print(f"Source: ({SOURCE_LAT}, {SOURCE_LON})")
    print(f"Target: ({TARGET_LAT}, {TARGET_LON})")
    
    print(f"\nLoading {DATASET}...")
    try:
        requests.post(f"{SERVER_URL}/load-dataset", json={"dataset": DATASET})
    except:
        pass
    time.sleep(1)
    
    # Test one-to-one
    test_route("one_to_one")
    
    # Test KNN n=1
    test_route("knn", num_candidates=1)
