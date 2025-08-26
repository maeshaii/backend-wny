import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import User, AccountType

def check_ojt_status():
    """Check OJT status of existing users"""
    
    print("🔍 Checking OJT Status...")
    print("=" * 40)
    
    # Get all OJT users
    ojt_users = User.objects.filter(account_type__ojt=True).order_by('user_id')
    
    print(f"📊 Total OJT Users: {ojt_users.count()}")
    print()
    
    for user in ojt_users:
        print(f"👤 {user.f_name} {user.l_name} (ID: {user.user_id})")
        print(f"   CTU ID: {user.acc_username}")
        print(f"   Course: {user.course}")
        print(f"   Year: {user.year_graduated}")
        print(f"   User Status: {user.user_status}")
        print(f"   OJT Status: {user.ojtstatus}")
        print(f"   Start Date: {user.date_started}")
        print(f"   End Date: {user.ojt_end_date}")
        print()
    
    # Check status distribution
    print("📈 Status Distribution:")
    status_counts = {}
    for user in ojt_users:
        status = user.ojtstatus or 'no_status'
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"   {status}: {count} users")
    
    # Check if any users have proper status
    users_with_status = ojt_users.exclude(ojtstatus__isnull=True).exclude(ojtstatus='')
    print(f"\n✅ Users with OJT status: {users_with_status.count()}")
    
    # Check if any users are in_progress (should show in coordinator view)
    in_progress_users = ojt_users.filter(ojtstatus='in_progress')
    print(f"🔄 Users in progress: {in_progress_users.count()}")
    
    # Check if any users are completed (should show in coordinator view)
    completed_users = ojt_users.filter(ojtstatus='completed')
    print(f"✅ Users completed: {completed_users.count()}")
    
    # Check if any users are pending (should show in admin view)
    pending_users = ojt_users.filter(ojtstatus='pending')
    print(f"⏳ Users pending: {pending_users.count()}")

if __name__ == '__main__':
    check_ojt_status()
