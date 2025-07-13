import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import User

def check_alumni_accounts():
    print("=== Alumni Accounts in Database ===")
    
    # Get all alumni accounts (user=True)
    alumni_accounts = User.objects.filter(account_type__user=True)
    
    print(f"Total Alumni Accounts: {alumni_accounts.count()}")
    print("\n=== Alumni Details ===")
    
    for i, alumni in enumerate(alumni_accounts, 1):
        print(f"{i}. CTU ID: {alumni.acc_username}")
        print(f"   Name: {alumni.f_name} {alumni.m_name or ''} {alumni.l_name}")
        print(f"   Gender: {alumni.gender}")
        print(f"   Birthdate: {alumni.acc_password}")
        print(f"   Course: {alumni.course or 'Not specified'}")
        print(f"   Year Graduated: {alumni.year_graduated or 'Not specified'}")
        print(f"   Phone: {alumni.phone_num or 'Not specified'}")
        print(f"   Status: {alumni.user_status}")
        print()

if __name__ == "__main__":
    check_alumni_accounts() 