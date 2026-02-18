
import requests
import sys

def verify_api():
    base_url = "http://localhost:8000"
    
    # Check Health
    try:
        resp = requests.get(f"{base_url}/health")
        if resp.status_code == 200:
            print("[PASS] Health Check: OK")
        else:
            print(f"[FAIL] Health Check: {resp.status_code}")
            sys.exit(1)
            
        # Check Jobs API
        resp = requests.get(f"{base_url}/api/jobs")
        if resp.status_code == 200:
            data = resp.json()
            # Depending on pagination, check 'items' or direct list
            print(f"[PASS] Jobs API: OK")
            print(f"  Response keys: {list(data.keys())}")
            
            items = data.get('items', [])
            print(f"  Jobs returned: {len(items)}")
            if len(items) > 0:
                print(f"  First job: {items[0]['title']}")
        else:
            print(f"[FAIL] Jobs API: {resp.status_code}")
            print(resp.text)
            sys.exit(1)
            
    except Exception as e:
        print(f"[FAIL] Connection Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_api()
