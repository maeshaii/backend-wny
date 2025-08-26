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

def test_ojt_import():
    """Test the OJT import process step by step"""
    
    print("🧪 Testing OJT Import Process...")
    print("=" * 50)
    
    # 1. Check OJT AccountType
    print("1️⃣ Checking OJT AccountType...")
    ojt_account_type = AccountType.objects.get(
        ojt=True, 
        admin=False, 
        peso=False, 
        user=False, 
        coordinator=False
    )
    print(f"   ✅ Found OJT AccountType ID: {ojt_account_type.account_type_id}")
    
    # 2. Test creating a sample OJT user
    print("\n2️⃣ Testing OJT User Creation...")
    try:
        test_ojt_user = User.objects.create(
            acc_username='TEST_OJT_001',
            acc_password=date(2000, 1, 1),
            birthdate=date(2000, 1, 1),
            age=24,
            user_status='active',
            f_name='Test',
            m_name='',
            l_name='OJTUser',
            gender='M',
            phone_num='',
            address='',
            civil_status='',
            social_media='',
            year_graduated=2024,
            course='BSIT',
            account_type=ojt_account_type
        )
        
        print(f"   ✅ Successfully created test OJT user:")
        print(f"      ID: {test_ojt_user.user_id}")
        print(f"      Username: {test_ojt_user.acc_username}")
        print(f"      Name: {test_ojt_user.f_name} {test_ojt_user.l_name}")
        print(f"      Account Type: OJT")
        
        # Clean up - delete the test user
        test_ojt_user.delete()
        print(f"   🧹 Test user deleted for cleanup")
        
    except Exception as e:
        print(f"   ❌ Error creating test OJT user: {e}")
        return False
    
    # 3. Check if there are any existing OJT users
    print("\n3️⃣ Checking Existing OJT Users...")
    existing_ojt_users = User.objects.filter(account_type=ojt_account_type)
    print(f"   📊 Total OJT users: {existing_ojt_users.count()}")
    
    if existing_ojt_users.exists():
        print("   📋 Existing OJT Users:")
        for user in existing_ojt_users[:5]:  # Show first 5
            print(f"      - {user.acc_username}: {user.f_name} {user.l_name}")
    
    # 4. Check the import requirements
    print("\n4️⃣ Checking Import Requirements...")
    print("   Required Excel columns: CTU_ID, First_Name, Last_Name, Gender, Birthdate")
    print("   Optional columns: Ojt_Start_Date, Ojt_End_Date, Phone_Number, Address, Civil_Status, Social_Media")
    print("   Required POST data: batch_year, course, coordinator_username")
    
    return True

if __name__ == '__main__':
    test_ojt_import()
