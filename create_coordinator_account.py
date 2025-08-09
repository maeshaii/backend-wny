#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import User, AccountType

def create_coordinator_account():
    try:
        # Check if coordinator account type exists, if not create it
        coordinator_account_type, created = AccountType.objects.get_or_create(
            coordinator=True,
            defaults={
                'admin': False,
                'peso': False,
                'user': False,
                'ojt': False
            }
        )
        
        if created:
            print(f"✅ Created new coordinator account type")
        else:
            print(f"✅ Using existing coordinator account type")
        
        # Delete existing coordinator user if present
        User.objects.filter(acc_username='coordinator').delete()
        
        # Check if user already exists
        username = 'coordinator'
        if User.objects.filter(acc_username=username).exists():
            print(f"❌ User with username '{username}' already exists!")
            return
        
        # Create the coordinator user
        # Convert password "january,1,2001" to date format
        password_date = datetime.strptime('2001-01-01', '%Y-%m-%d').date()
        
        coordinator_user = User.objects.create(
            account_type=coordinator_account_type,
            acc_username=username,
            acc_password=password_date,
            user_status='active',
            f_name='Coordinator',
            l_name='User',
            gender='Not specified'
        )
        
        print(f"✅ Successfully created coordinator account!")
        print(f"   Username: {coordinator_user.acc_username}")
        print(f"   Password: january,1,2001 (stored as date: {coordinator_user.acc_password})")
        print(f"   Account Type: Coordinator")
        print(f"   Status: {coordinator_user.user_status}")
        
    except Exception as e:
        print(f"❌ Error creating coordinator account: {e}")

if __name__ == '__main__':
    create_coordinator_account() 