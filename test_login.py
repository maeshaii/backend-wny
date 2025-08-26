import requests
import json

def test_login():
    url = "http://127.0.0.1:8000/api/login/"
    
    # Test data with correct format
    data = {
        "acc_username": "coordinator",
        "acc_password": "11/03/2002"  # MM/DD/YYYY format
    }
    
    headers = {
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Login successful!")
                print(f"User: {result.get('user', {}).get('name')}")
                print(f"Account type: {result.get('user', {}).get('account_type')}")
            else:
                print("❌ Login failed")
        else:
            print("❌ Request failed")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_login()
