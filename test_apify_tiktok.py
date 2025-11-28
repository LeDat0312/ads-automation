#!/usr/bin/env python3
"""
Test script để gọi Apify TikTok actor trực tiếp
NOTE: Chạy trên VPS để test
"""

import requests
import json
import sys

# Config
APIFY_TOKEN = os.getenv("APIFY_DEFAULT_KEY", "")
# hoặc nếu muốn test nhanh:
# raise ValueError("Set APIFY_DEFAULT_KEY in .env before running this test")
ACTOR_ID = "clockworks~free-tiktok-scraper"
TEST_URL = "https://www.tiktok.com/@nangmui.hoangduong/video/7536470562428800263"

def test_sync_endpoint():
    """Test endpoint run-sync-get-dataset-items"""
    print("=" * 60)
    print("Testing: run-sync-get-dataset-items")
    print("=" * 60)
    
    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items?token={APIFY_KEY}"
    
    payload = {
        "postURLs": [TEST_URL],
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
    }
    
    print(f"\nURL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nSending request...")
    
    try:
        resp = requests.post(url, json=payload, timeout=180)
        
        print(f"\nStatus Code: {resp.status_code}")
        print(f"Headers: {dict(resp.headers)}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                print(f"\nResponse Type: {type(data)}")
                print(f"Response Length: {len(data) if isinstance(data, list) else 'N/A'}")
                print(f"\nResponse Preview:")
                print(json.dumps(data[:1] if isinstance(data, list) and data else data, indent=2)[:1000])
                
                if isinstance(data, list) and data:
                    item = data[0]
                    print(f"\n✅ SUCCESS! Got item with keys: {list(item.keys())}")
                    print(f"\nItem details:")
                    print(f"  - text: {item.get('text', 'N/A')[:100]}")
                    print(f"  - webVideoUrl: {item.get('webVideoUrl', 'N/A')}")
                    print(f"  - video: {item.get('video', 'N/A')}")
                else:
                    print("\n❌ FAILED: Empty or invalid response")
                    
            except Exception as e:
                print(f"\n❌ JSON Parse Error: {e}")
                print(f"Raw response: {resp.text[:500]}")
        else:
            print(f"\n❌ HTTP Error: {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
            
    except Exception as e:
        print(f"\n❌ Request Error: {e}")
        import traceback
        traceback.print_exc()


def test_async_endpoint():
    """Test endpoint /runs (async)"""
    print("\n" + "=" * 60)
    print("Testing: /runs (async)")
    print("=" * 60)
    
    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_KEY}"
    
    payload = {
        "postURLs": [TEST_URL],
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
    }
    
    print(f"\nURL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nSending request...")
    
    try:
        resp = requests.post(url, json=payload, timeout=30)
        
        print(f"\nStatus Code: {resp.status_code}")
        
        if resp.status_code == 201:
            data = resp.json().get("data", {})
            run_id = data.get("id")
            dataset_id = data.get("defaultDatasetId")
            
            print(f"\n✅ Run started!")
            print(f"  - Run ID: {run_id}")
            print(f"  - Dataset ID: {dataset_id}")
            
            if dataset_id:
                print(f"\nTo fetch dataset items, use:")
                print(f"GET https://api.apify.com/v2/datasets/{dataset_id}/items?token=...")
        else:
            print(f"\n❌ HTTP Error: {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
            
    except Exception as e:
        print(f"\n❌ Request Error: {e}")


if __name__ == "__main__":
    print("🚀 Apify TikTok Actor Test")
    print(f"Actor: {ACTOR_ID}")
    print(f"Test URL: {TEST_URL}")
    print()
    
    # Test sync endpoint first (this is what we're using)
    test_sync_endpoint()
    
    # Optionally test async
    if "--async" in sys.argv:
        test_async_endpoint()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
