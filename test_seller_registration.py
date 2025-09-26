#!/usr/bin/env python3
"""
Test script to verify seller registration works correctly
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_seller_registration():
    """Test seller registration endpoint"""
    
    # Test data for seller registration
    seller_data = {
        "email": "test_seller@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "Seller",
        "phone": "9876543210",
        "business_name": "Test Electronics Store",
        "business_type": "Electronics Retail",
        "address": "456 Test Street, Test City",
        "city": "Delhi",
        "state": "Delhi",
        "pincode": "110001"
    }
    
    print("🧪 Testing Seller Registration...")
    print(f"📤 Sending POST request to: {BASE_URL}/api/v1/auth/register/seller")
    print(f"📋 Data: {json.dumps(seller_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register/seller",
            json=seller_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📄 Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Seller registration successful!")
            
            # Test login with the new seller
            login_data = {
                "email": seller_data["email"],
                "password": seller_data["password"]
            }
            
            print(f"\n🔐 Testing login with new seller...")
            login_response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                print("✅ Seller login successful!")
                token_data = login_response.json()
                access_token = token_data["access_token"]
                
                # Test getting user info
                print(f"\n👤 Testing user info retrieval...")
                user_response = requests.get(
                    f"{BASE_URL}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if user_response.status_code == 200:
                    user_info = user_response.json()
                    print("✅ User info retrieved successfully!")
                    print(f"📊 User Info: {json.dumps(user_info, indent=2)}")
                    print(f"👤 Role: {user_info.get('role')}")
                    print(f"🏢 Business: Check database for seller details")
                else:
                    print(f"❌ Failed to get user info: {user_response.status_code}")
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"📄 Error: {login_response.json()}")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"📄 Error: {response.json()}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_seller_registration() 