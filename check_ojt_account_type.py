import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.shared.models import AccountType

def check_ojt_account_type():
    """Check the exact boolean values of the OJT AccountType"""
    
    ojt_account_type = AccountType.objects.filter(ojt=True).first()
    if ojt_account_type:
        print(f"🔍 OJT AccountType Details:")
        print(f"  ID: {ojt_account_type.account_type_id}")
        print(f"  admin: {ojt_account_type.admin}")
        print(f"  peso: {ojt_account_type.peso}")
        print(f"  user: {ojt_account_type.user}")
        print(f"  coordinator: {ojt_account_type.coordinator}")
        print(f"  ojt: {ojt_account_type.ojt}")
        
        # Test the query that's failing in the import
        print(f"\n🧪 Testing the import query:")
        try:
            test_query = AccountType.objects.get(
                ojt=True, 
                admin=False, 
                peso=False, 
                user=False, 
                coordinator=False
            )
            print(f"  ✅ Query SUCCESS: Found AccountType ID {test_query.account_type_id}")
        except AccountType.DoesNotExist:
            print(f"  ❌ Query FAILED: No AccountType found with exact boolean values")
            
            # Show what we actually have
            print(f"\n📋 Available AccountTypes:")
            for at in AccountType.objects.all():
                print(f"  ID {at.account_type_id}: admin={at.admin}, peso={at.peso}, user={at.user}, coordinator={at.coordinator}, ojt={at.ojt}")
    else:
        print("❌ No OJT AccountType found!")

if __name__ == '__main__':
    check_ojt_account_type()
