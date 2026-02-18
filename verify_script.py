import urllib.request
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def make_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if data:
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)
    except Exception as e:
        print(f"Request failed: {e}")
        return None, None

def main():
    print("Waiting for API to be ready...")
    for _ in range(30):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    print("API is ready.")
                    break
        except:
            time.sleep(2)
    else:
        print("API failed to become ready.")
        sys.exit(1)

    # 1. Submit OK content
    print("\n--- Submitting OK Content ---")
    status, body = make_request("POST", "/api/v1/content/submit", {"userId": "alice", "text": "This is a clean post"})
    print(f"Status: {status}, Body: {body}")
    
    if status != 202:
        print("Failed to submit content")
        sys.exit(1)
    
    content_id = body["contentId"]
    
    # 2. Check Status
    print(f"\n--- Checking Status for {content_id} ---")
    # Wait for processor
    time.sleep(2) 
    status, body = make_request("GET", f"/api/v1/content/{content_id}/status")
    print(f"Status: {status}, Body: {body}")
    
    if body["status"] != "APPROVED":
        print(f"Expected APPROVED, got {body['status']}")

    # 3. Submit Bad Content
    print("\n--- Submitting Bad Content ---")
    status, body = make_request("POST", "/api/v1/content/submit", {"userId": "bob", "text": "This contains a badword"})
    print(f"Status: {status}, Body: {body}")
    content_id_bad = body["contentId"]
    
    print(f"\n--- Checking Status for {content_id_bad} ---")
    time.sleep(2)
    status, body = make_request("GET", f"/api/v1/content/{content_id_bad}/status")
    print(f"Status: {status}, Body: {body}")

    if body["status"] != "REJECTED":
         print(f"Expected REJECTED, got {body['status']}")

    # 4. Trigger Rate Limit
    print("\n--- Triggering Rate Limit ---")
    user_id = "spammer"
    for i in range(12):
        status, body = make_request("POST", "/api/v1/content/submit", {"userId": user_id, "text": "spam"})
        print(f"Request {i+1}: Status {status}")
        if status == 429:
            print("Rate limit triggered successfully.")
            break
    else:
        print("Failed to trigger rate limit.")

if __name__ == "__main__":
    main()
