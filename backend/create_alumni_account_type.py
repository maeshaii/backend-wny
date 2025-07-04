import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import AccountType

def create_alumni_account_type():
    # Check if alumni account type already exists
    try:
        existing_alumni = AccountType.objects.get(user=True, admin=False, peso=False, coordinator=False)
        print(f"Alumni account type already exists with ID: {existing_alumni.account_type_id}")
        return existing_alumni
    except AccountType.DoesNotExist:
        pass
    
    # Create new alumni account type
    alumni_account_type = AccountType.objects.create(
        admin=False,
        user=True,
        peso=False,
        coordinator=False
    )
    
    print(f"Successfully created alumni account type with ID: {alumni_account_type.account_type_id}")
    return alumni_account_type

if __name__ == "__main__":
    create_alumni_account_type() 