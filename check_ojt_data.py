import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import User, AccountType

def check_ojt_data():
    """Check what OJT data exists in the database"""
    
    print("🔍 Checking OJT Data in Database...")
    print("=" * 50)
    
    # Check OJT AccountType
    ojt_account_type = AccountType.objects.filter(ojt=True).first()
    if ojt_account_type:
        print(f"✅ OJT AccountType found: ID {ojt_account_type.account_type_id}")
    else:
        print("❌ No OJT AccountType found!")
        return
    
    # Check OJT Users
    ojt_users = User.objects.filter(account_type=ojt_account_type)
    print(f"\n👥 OJT Users: {ojt_users.count()}")
    
    if ojt_users.exists():
        print("\n📋 OJT User Details:")
        for i, user in enumerate(ojt_users[:10], 1):  # Show first 10
            print(f"  {i}. ID: {user.user_id}")
            print(f"     Username: {user.acc_username}")
            print(f"     Name: {user.f_name} {user.l_name}")
            print(f"     Course: {user.course}")
            print(f"     Year: {user.year_graduated}")
            print(f"     Status: {user.user_status}")
            print(f"     OJT End Date: {user.ojt_end_date}")
            print()
    else:
        print("❌ No OJT users found!")
    
    # Check all users by account type
    print("\n📊 All Users by Account Type:")
    for account_type in AccountType.objects.all():
        user_count = User.objects.filter(account_type=account_type).count()
        type_name = []
        if account_type.admin: type_name.append('Admin')
        if account_type.peso: type_name.append('PESO')
        if account_type.user: type_name.append('User')
        if account_type.coordinator: type_name.append('Coordinator')
        if account_type.ojt: type_name.append('OJT')
        
        print(f"  {', '.join(type_name)}: {user_count} users")
    
    # Check if there are any users at all
    total_users = User.objects.count()
    print(f"\n📈 Total Users in Database: {total_users}")
    
    # Check the last few users created
    print(f"\n🕒 Recent Users (last 5):")
    recent_users = User.objects.order_by('-user_id')[:5]
    for user in recent_users:
        type_name = []
        if user.account_type.admin: type_name.append('Admin')
        if user.account_type.peso: type_name.append('PESO')
        if user.account_type.user: type_name.append('User')
        if user.account_type.coordinator: type_name.append('Coordinator')
        if user.account_type.ojt: type_name.append('OJT')
        
        print(f"  ID {user.user_id}: {user.acc_username} ({', '.join(type_name)}) - {user.f_name} {user.l_name}")

if __name__ == '__main__':
    check_ojt_data()
