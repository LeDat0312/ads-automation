#!/usr/bin/env python3
"""
Script để kiểm tra các API endpoints của settings page
"""
import requests
import json
import sys
from urllib.parse import urljoin

BASE_URL = "https://updatemetaads.site"

def check_endpoint(url, headers=None, method="GET", data=None):
    """Kiểm tra một endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            print(f"❌ Method {method} not supported")
            return False
        
        print(f"\n{'='*60}")
        print(f"URL: {url}")
        print(f"Method: {method}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Response OK")
                print(f"Response (first 200 chars): {str(data)[:200]}")
                return True
            except:
                print(f"⚠️ Response is not JSON")
                print(f"Response (first 200 chars): {response.text[:200]}")
                return False
        else:
            print(f"❌ Error Response")
            print(f"Response (first 500 chars): {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🔍 Checking Settings API Endpoints...")
    print(f"Base URL: {BASE_URL}")
    
    # Note: Các endpoints này cần authentication
    # Nếu không có token, sẽ trả về 401/403
    endpoints = [
        ("/settings/token/status", "GET"),
        ("/settings/accounts", "GET"),
        ("/settings/prefixes", "GET"),
    ]
    
    results = []
    for endpoint, method in endpoints:
        url = urljoin(BASE_URL, endpoint)
        success = check_endpoint(url, method=method)
        results.append((endpoint, success))
    
    print(f"\n{'='*60}")
    print("📊 Summary:")
    for endpoint, success in results:
        status = "✅ OK" if success else "❌ FAILED"
        print(f"  {status}: {endpoint}")
    
    print("\n💡 Note: Nếu các endpoints trả về 401/403, bạn cần đăng nhập trước.")
    print("   Mở browser, đăng nhập vào website, sau đó:")
    print("   1. Mở Developer Console (F12)")
    print("   2. Vào tab 'Network'")
    print("   3. Reload trang /settings")
    print("   4. Xem các requests và responses")

if __name__ == "__main__":
    main()

