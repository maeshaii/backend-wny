#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import and run the function
from apps.ojt_stats.views import create_ojt_profiles_for_existing_users

if __name__ == "__main__":
    result = create_ojt_profiles_for_existing_users()
    print(f"\nScript completed successfully!")
    print(f"Created: {result['created_count']} profiles")
    print(f"Total profiles: {result['total_profiles']}")
    print(f"Completed profiles: {result['completed_profiles']}") 