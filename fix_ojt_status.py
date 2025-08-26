import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import User, AccountType

def fix_ojt_status():
    """Fix OJT status of existing users"""
    
    print("🔧 Fixing OJT Status...")
    print("=" * 40)
    
    # Get all OJT users with no status
    ojt_users_no_status = User.objects.filter(
        account_type__ojt=True,
        ojtstatus__isnull=True
    )
    
    print(f"📊 OJT users with no status: {ojt_users_no_status.count()}")
    
    if ojt_users_no_status.exists():
        # Update all users to in_progress status
        updated_count = ojt_users_no_status.update(ojtstatus='in_progress')
        print(f"✅ Updated {updated_count} users to 'in_progress' status")
        
        # Show the updated users
        print("\n📋 Updated Users:")
        for user in ojt_users_no_status:
            print(f"   - {user.f_name} {user.l_name} (ID: {user.user_id})")
    else:
        print("✅ All OJT users already have proper status")
    
    # Final status check
    print("\n📈 Final Status Distribution:")
    ojt_users = User.objects.filter(account_type__ojt=True)
    
    status_counts = {}
    for user in ojt_users:
        status = user.ojtstatus or 'no_status'
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"   {status}: {count} users")
    
    # Check coordinator view should show
    in_progress_users = ojt_users.filter(ojtstatus='in_progress')
    print(f"\n🔄 Users that should show in coordinator view: {in_progress_users.count()}")

if __name__ == '__main__':
    fix_ojt_status()
