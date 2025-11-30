"""
Test script for Facebook Account (Via Token) Management API
Requires a valid user token for authentication

Usage:
    python test_facebook_via_api.py
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
# TODO: Replace with your actual user token after login
USER_TOKEN = "YOUR_TOKEN_HERE"

HEADERS = {
    "Authorization": f"Bearer {USER_TOKEN}",
    "Content-Type": "application/json"
}


def print_response(response: requests.Response, title: str):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response Text: {response.text}")
    
    print(f"{'='*60}\n")


def test_list_accounts():
    """Test GET /api/facebook-accounts"""
    print("📋 Testing: List all Facebook accounts")
    
    # Test without filters
    response = requests.get(f"{BASE_URL}/api/facebook-accounts", headers=HEADERS)
    print_response(response, "List All Accounts")
    
    # Test with type filter
    response = requests.get(
        f"{BASE_URL}/api/facebook-accounts",
        headers=HEADERS,
        params={"type": "fanpage"}
    )
    print_response(response, "List Fanpage Accounts Only")
    
    # Test with is_active filter
    response = requests.get(
        f"{BASE_URL}/api/facebook-accounts",
        headers=HEADERS,
        params={"is_active": "true"}
    )
    print_response(response, "List Active Accounts Only")


def test_create_account():
    """Test POST /api/facebook-accounts"""
    print("➕ Testing: Create new Facebook account")
    
    # Test with invalid token (should fail)
    invalid_data = {
        "name": "Test Via - Invalid Token",
        "access_token": "INVALID_TOKEN_123",
        "token_type": "fanpage"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/facebook-accounts",
        headers=HEADERS,
        json=invalid_data
    )
    print_response(response, "Create Account (Invalid Token)")
    
    # Test with valid token (replace with actual token)
    print("\n⚠️ SKIPPED: Create with valid token")
    print("   Reason: Requires real Facebook token")
    print("   To test manually:")
    print("   1. Get a Facebook token from https://developers.facebook.com/tools/explorer/")
    print("   2. Replace VALID_FB_TOKEN below")
    print("   3. Uncomment the code\n")
    
    # UNCOMMENT TO TEST WITH REAL TOKEN:
    # valid_data = {
    #     "name": "Test Via - Valid Token",
    #     "access_token": "VALID_FB_TOKEN_HERE",
    #     "token_type": "fanpage"
    # }
    # response = requests.post(
    #     f"{BASE_URL}/api/facebook-accounts",
    #     headers=HEADERS,
    #     json=valid_data
    # )
    # print_response(response, "Create Account (Valid Token)")
    # return response.json().get("id")  # Return created ID for further tests


def test_get_account(account_id: str):
    """Test GET /api/facebook-accounts/{id}"""
    print(f"🔍 Testing: Get account by ID ({account_id})")
    
    response = requests.get(
        f"{BASE_URL}/api/facebook-accounts/{account_id}",
        headers=HEADERS
    )
    print_response(response, f"Get Account {account_id}")


def test_update_account(account_id: str):
    """Test PATCH /api/facebook-accounts/{id}"""
    print(f"✏️ Testing: Update account ({account_id})")
    
    update_data = {
        "name": "Updated Via Name",
        "is_active": False
    }
    
    response = requests.patch(
        f"{BASE_URL}/api/facebook-accounts/{account_id}",
        headers=HEADERS,
        json=update_data
    )
    print_response(response, f"Update Account {account_id}")


def test_verify_token(account_id: str):
    """Test POST /api/facebook-accounts/{id}/verify"""
    print(f"✅ Testing: Verify token ({account_id})")
    
    response = requests.post(
        f"{BASE_URL}/api/facebook-accounts/{account_id}/verify",
        headers=HEADERS
    )
    print_response(response, f"Verify Token {account_id}")


def test_get_pages(account_id: str):
    """Test GET /api/facebook-accounts/{id}/pages"""
    print(f"📄 Testing: Get pages from account ({account_id})")
    
    response = requests.get(
        f"{BASE_URL}/api/facebook-accounts/{account_id}/pages",
        headers=HEADERS
    )
    print_response(response, f"Get Pages from {account_id}")


def test_delete_account(account_id: str):
    """Test DELETE /api/facebook-accounts/{id}"""
    print(f"🗑️ Testing: Delete account ({account_id})")
    
    response = requests.delete(
        f"{BASE_URL}/api/facebook-accounts/{account_id}",
        headers=HEADERS
    )
    print_response(response, f"Delete Account {account_id}")


def test_channel_from_saved_account():
    """Test POST /api/channels/facebook/from-saved-account"""
    print("🔗 Testing: Create channels from saved account")
    
    print("\n⚠️ SKIPPED: Requires existing Facebook account ID")
    print("   To test manually:")
    print("   1. Create a Facebook account first")
    print("   2. Replace ACCOUNT_ID and PAGE_IDS below")
    print("   3. Uncomment the code\n")
    
    # UNCOMMENT TO TEST:
    # data = {
    #     "facebook_account_id": "ACCOUNT_ID_HERE",
    #     "page_ids": ["PAGE_ID_1", "PAGE_ID_2"]
    # }
    # response = requests.post(
    #     f"{BASE_URL}/api/channels/facebook/from-saved-account",
    #     headers=HEADERS,
    #     json=data
    # )
    # print_response(response, "Create Channels from Saved Account")


def test_manual_channel_v2():
    """Test POST /api/channels/facebook/manual-v2"""
    print("📝 Testing: Create channel manually (V2)")
    
    # Test without facebook_account_id (using app token)
    data_no_via = {
        "page_id": "123456789"  # Replace with real page ID
    }
    
    response = requests.post(
        f"{BASE_URL}/api/channels/facebook/manual-v2",
        headers=HEADERS,
        json=data_no_via
    )
    print_response(response, "Manual Channel V2 (No Via)")
    
    # Test with facebook_account_id (using saved token)
    print("\n⚠️ SKIPPED: Manual V2 with Via")
    print("   To test manually:")
    print("   1. Create a Facebook account first")
    print("   2. Replace ACCOUNT_ID below")
    print("   3. Uncomment the code\n")
    
    # UNCOMMENT TO TEST:
    # data_with_via = {
    #     "page_id": "123456789",
    #     "facebook_account_id": "ACCOUNT_ID_HERE"
    # }
    # response = requests.post(
    #     f"{BASE_URL}/api/channels/facebook/manual-v2",
    #     headers=HEADERS,
    #     json=data_with_via
    # )
    # print_response(response, "Manual Channel V2 (With Via)")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 FACEBOOK VIA TOKEN API TESTS")
    print("="*60)
    
    if USER_TOKEN == "YOUR_TOKEN_HERE":
        print("\n❌ ERROR: Please set USER_TOKEN first!")
        print("\nHow to get a token:")
        print("1. Start the backend: python -m uvicorn app.main:app --reload")
        print("2. Go to http://localhost:8000/docs")
        print("3. Click 'Authorize' and login")
        print("4. Copy the token from browser developer tools (localStorage)")
        print("   OR use the /auth/login endpoint")
        print("\nExample:")
        print('   USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."')
        return
    
    # Test basic CRUD
    test_list_accounts()
    
    # These tests require real data:
    # created_id = test_create_account()
    # if created_id:
    #     test_get_account(created_id)
    #     test_verify_token(created_id)
    #     test_get_pages(created_id)
    #     test_update_account(created_id)
    #     test_delete_account(created_id)
    
    # Test channel endpoints
    test_channel_from_saved_account()
    test_manual_channel_v2()
    
    print("\n" + "="*60)
    print("✅ Tests completed!")
    print("="*60)
    print("\n📝 Note: Some tests are skipped because they require:")
    print("   - Real Facebook access tokens")
    print("   - Existing Facebook account IDs")
    print("   - Valid page IDs")
    print("\n   See comments in code to enable these tests.")


if __name__ == "__main__":
    main()
