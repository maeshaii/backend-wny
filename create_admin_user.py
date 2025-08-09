import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import User, AccountType

USERNAME = 'admin'
PASSWORD = '2002-11-03'  # november-3-2002 in YYYY-MM-DD format
FIRST_NAME = 'Admin'
LAST_NAME = 'User'
GENDER = 'Other'
USER_STATUS = 'active'

def main():
    # Ensure AccountType with admin=True exists
    admin_type, created = AccountType.objects.get_or_create(
        admin=True,
        defaults={
            'peso': False,
            'user': False,
            'coordinator': False,
        }
    )

    # Check if user already exists
    if User.objects.filter(acc_username=USERNAME).exists():
        print(f"User '{USERNAME}' already exists.")
    else:
        user = User.objects.create(
            acc_username=USERNAME,
            acc_password=datetime.strptime(PASSWORD, '%Y-%m-%d'),
            account_type=admin_type,
            user_status=USER_STATUS,
            f_name=FIRST_NAME,
            l_name=LAST_NAME,
            gender=GENDER,
        )
        print(f"Admin user '{USERNAME}' created successfully with password date: {PASSWORD}")

if __name__ == "__main__":
    main() 