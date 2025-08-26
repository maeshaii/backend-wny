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

def create_admin_user():
    """Create an admin user account"""
    
    print("🔧 Creating Admin User Account...")
    print("=" * 50)
    
    # Get the admin account type
    admin_account_type = AccountType.objects.filter(admin=True).first()
    if not admin_account_type:
        print("❌ No Admin AccountType found! Creating one...")
        admin_account_type = AccountType.objects.create(
            admin=True,
            peso=False,
            user=False,
            coordinator=False,
            ojt=False
        )
        print(f"✅ Created Admin AccountType with ID: {admin_account_type.account_type_id}")
    else:
        print(f"✅ Found Admin AccountType with ID: {admin_account_type.account_type_id}")
    
    # Check if admin user already exists
    existing_admin = User.objects.filter(account_type=admin_account_type).first()
    if existing_admin:
        print(f"✅ Admin user already exists:")
        print(f"   Username: {existing_admin.acc_username}")
        print(f"   Name: {existing_admin.f_name} {existing_admin.l_name}")
        print(f"   Password (birthdate): {existing_admin.acc_password}")
        return
    
    # Create admin user
    try:
        admin_user = User.objects.create(
            acc_username='admin',
            acc_password=date(1990, 1, 1),  # Default birthdate: January 1, 1990
            birthdate=date(1990, 1, 1),
            age=34,
            user_status='active',
            f_name='System',
            m_name='',
            l_name='Administrator',
            gender='M',
            phone_num='',
            address='',
            civil_status='',
            social_media='',
            year_graduated=2020,
            course='Computer Science',
            account_type=admin_account_type
        )
        
        print(f"✅ Successfully created admin user with ID: {admin_user.user_id}")
        print(f"   Username: {admin_user.acc_username}")
        print(f"   Password (birthdate): {admin_user.acc_password}")
        print(f"   Name: {admin_user.f_name} {admin_user.l_name}")
        print(f"   Account Type: Admin")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

if __name__ == '__main__':
    create_admin_user() 