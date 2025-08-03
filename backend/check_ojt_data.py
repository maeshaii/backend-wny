#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import User
from apps.ojt_users.models import OjtUser

print("=== Checking OJT Data ===")

# Check total users
total_users = User.objects.count()
print(f"Total users: {total_users}")

# Check users with OJT account type
ojt_users = User.objects.filter(account_type__ojt=True)
print(f"Users with OJT account type: {ojt_users.count()}")

# Check OjtUser profiles
ojt_profiles = OjtUser.objects.all()
print(f"OjtUser profiles: {ojt_profiles.count()}")

# Check OJT statuses
if ojt_profiles.exists():
    print("\nOJT Status breakdown:")
    status_counts = {}
    for profile in ojt_profiles:
        status = profile.ojt_status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    # Check completed OJT records
    completed_ojt = ojt_profiles.filter(ojt_status='completed')
    print(f"\nCompleted OJT records: {completed_ojt.count()}")
    
    if completed_ojt.exists():
        print("\nSample completed OJT records:")
        for i, profile in enumerate(completed_ojt[:5]):
            user = profile.user
            print(f"  {i+1}. {user.f_name} {user.l_name} - {user.acc_username}")
    else:
        print("\nNo completed OJT records found!")
        print("Available statuses:", list(status_counts.keys()))

# Check if there are any users without OjtUser profiles
users_without_profiles = []
for user in ojt_users:
    try:
        user.ojt_profile
    except:
        users_without_profiles.append(user)

if users_without_profiles:
    print(f"\nUsers without OjtUser profiles: {len(users_without_profiles)}")
    for user in users_without_profiles[:5]:
        print(f"  - {user.f_name} {user.l_name} ({user.acc_username})")

print("\n=== End of OJT Data Check ===") 