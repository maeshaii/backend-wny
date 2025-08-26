import os
import sys
import django
from datetime import date

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import User

def check_coordinator():
    try:
        # Find the coordinator user
        coordinator = User.objects.filter(acc_username='coordinator').first()
        if coordinator:
            print(f"Coordinator user found:")
            print(f"  Username: {coordinator.acc_username}")
            print(f"  Password (birthdate): {coordinator.acc_password}")
            print(f"  Account type: {coordinator.account_type.coordinator}")
            print(f"  Status: {coordinator.user_status}")
            
            # Test different date formats
            test_dates = [
                "11/03/2002",  # MM/DD/YYYY
                "2002-11-03",  # YYYY-MM-DD
                "03/11/2002",  # DD/MM/YYYY
            ]
            
            print("\nTesting login with different date formats:")
            for test_date in test_dates:
                try:
                    if "/" in test_date:
                        # Parse MM/DD/YYYY or DD/MM/YYYY
                        parts = test_date.split("/")
                        if len(parts) == 3:
                            # Try MM/DD/YYYY first
                            try:
                                parsed_date = date(int(parts[2]), int(parts[0]), int(parts[1]))
                                if parsed_date == coordinator.acc_password:
                                    print(f"  ✅ {test_date} (MM/DD/YYYY) - MATCHES")
                                else:
                                    print(f"  ❌ {test_date} (MM/DD/YYYY) - No match")
                            except ValueError:
                                print(f"  ❌ {test_date} - Invalid date")
                    else:
                        # Parse YYYY-MM-DD
                        try:
                            parsed_date = date.fromisoformat(test_date)
                            if parsed_date == coordinator.acc_password:
                                print(f"  ✅ {test_date} - MATCHES")
                            else:
                                print(f"  ❌ {test_date} - No match")
                        except ValueError:
                            print(f"  ❌ {test_date} - Invalid date")
                            
                except Exception as e:
                    print(f"  ❌ {test_date} - Error: {e}")
                    
        else:
            print("No coordinator user found!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_coordinator()
