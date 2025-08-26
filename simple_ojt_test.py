import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import User, AccountType
from datetime import date

def simple_ojt_test():
    """Simple test to create an OJT user"""
    
    print("🧪 Simple OJT Test...")
    print("=" * 30)
    
    # Get OJT AccountType
    ojt_account_type = AccountType.objects.filter(ojt=True).first()
    if not ojt_account_type:
        print("❌ No OJT AccountType found!")
        return
    
    print(f"✅ Found OJT AccountType ID: {ojt_account_type.account_type_id}")
    
    # Check existing OJT users
    existing_count = User.objects.filter(account_type=ojt_account_type).count()
    print(f"📊 Current OJT users: {existing_count}")
    
    # Try to create a simple OJT user
    try:
        test_user = User.objects.create(
            acc_username='TEST001',
            acc_password=date(2000, 1, 1),
            user_status='active',
            f_name='Test',
            l_name='User',
            gender='M',
            account_type=ojt_account_type,
            ojtstatus='in_progress'
        )
        
        print(f"✅ Successfully created test user:")
        print(f"   ID: {test_user.user_id}")
        print(f"   Username: {test_user.acc_username}")
        print(f"   OJT Status: {test_user.ojtstatus}")
        
        # Clean up
        test_user.delete()
        print("🧹 Test user deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    simple_ojt_test()
