import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import AccountType

def create_account_types():
    """Create all necessary account types for the system"""
    
    # Define all the account types we need
    account_types = [
        {
            'admin': True,
            'peso': False,
            'user': False,
            'coordinator': False,
            'ojt': False,
            'description': 'Administrator'
        },
        {
            'admin': False,
            'peso': True,
            'user': False,
            'coordinator': False,
            'ojt': False,
            'description': 'PESO'
        },
        {
            'admin': False,
            'peso': False,
            'user': True,
            'coordinator': False,
            'ojt': False,
            'description': 'Alumni User'
        },
        {
            'admin': False,
            'peso': False,
            'user': False,
            'coordinator': True,
            'ojt': False,
            'description': 'Coordinator'
        },
        {
            'admin': False,
            'peso': False,
            'user': False,
            'coordinator': False,
            'ojt': True,
            'description': 'OJT User'
        }
    ]
    
    created_count = 0
    existing_count = 0
    
    for account_type_data in account_types:
        # Remove description before creating the object
        description = account_type_data.pop('description')
        
        # Check if this account type already exists
        existing = AccountType.objects.filter(
            admin=account_type_data['admin'],
            peso=account_type_data['peso'],
            user=account_type_data['user'],
            coordinator=account_type_data['coordinator'],
            ojt=account_type_data['ojt']
        ).first()
        
        if existing:
            print(f"✅ {description} - Already exists (ID: {existing.account_type_id})")
            existing_count += 1
        else:
            # Create the account type
            new_account_type = AccountType.objects.create(**account_type_data)
            print(f"🆕 {description} - Created with ID: {new_account_type.account_type_id}")
            created_count += 1
        
        # Add description back for the next iteration
        account_type_data['description'] = description
    
    print(f"\n📊 Summary:")
    print(f"   Created: {created_count}")
    print(f"   Already existed: {existing_count}")
    print(f"   Total: {created_count + existing_count}")
    
    # List all existing account types
    print(f"\n📋 All Account Types:")
    all_types = AccountType.objects.all().order_by('account_type_id')
    for at in all_types:
        type_name = []
        if at.admin: type_name.append('Admin')
        if at.peso: type_name.append('PESO')
        if at.user: type_name.append('User')
        if at.coordinator: type_name.append('Coordinator')
        if at.ojt: type_name.append('OJT')
        if not any([at.admin, at.peso, at.user, at.coordinator, at.ojt]):
            type_name.append('None')
        
        print(f"   ID {at.account_type_id}: {', '.join(type_name)}")

if __name__ == '__main__':
    create_account_types()
