import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import RequestFactory
from apps.api.views import coordinator_ojt_list_view
import json

def test_coordinator_api():
    """Test the coordinator OJT list API"""
    
    print("🧪 Testing Coordinator OJT API...")
    print("=" * 40)
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/ojt/coordinator/list/?coordinator=coordinator')
    
    # Call the view
    response = coordinator_ojt_list_view(request)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"Success: {data.get('success')}")
        print(f"Data Count: {len(data.get('data', []))}")
        
        print("\n📋 OJT Records:")
        for i, record in enumerate(data.get('data', [])[:5], 1):  # Show first 5
            print(f"  {i}. {record.get('name')} ({record.get('ctu_id')})")
            print(f"     Course: {record.get('course')}")
            print(f"     Status: {record.get('ojt_status')}")
            print(f"     Start Date: {record.get('date_started')}")
            print(f"     End Date: {record.get('ojt_end_date')}")
            print()
    else:
        print(f"Error: {response.content}")

if __name__ == '__main__':
    test_coordinator_api()
