from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Create your views here.

def create_ojt_profiles_for_existing_users():
    """
    Script to create OjtUser profiles for existing users with OJT account type
    and set their status to 'completed' for testing purposes
    """
    from apps.shared.models import User
    from apps.ojt_users.models import OjtUser
    
    print("=== Creating OjtUser Profiles ===")
    
    # Get users with OJT account type
    ojt_users = User.objects.filter(account_type__ojt=True)
    print(f"Found {ojt_users.count()} users with OJT account type")
    
    created_count = 0
    for user in ojt_users:
        try:
            # Check if OjtUser profile already exists
            existing_profile = OjtUser.objects.filter(user=user).first()
            
            if existing_profile:
                print(f"Profile already exists for {user.f_name} {user.l_name}")
                # Update status to completed if not already
                if existing_profile.ojt_status != 'completed':
                    existing_profile.ojt_status = 'completed'
                    existing_profile.save()
                    print(f"  -> Updated status to 'completed'")
            else:
                # Create new OjtUser profile
                ojt_profile = OjtUser.objects.create(
                    user=user,
                    ojt_status='completed'
                )
                created_count += 1
                print(f"Created profile for {user.f_name} {user.l_name} ({user.acc_username})")
                
        except Exception as e:
            print(f"Error creating profile for {user.f_name} {user.l_name}: {e}")
    
    print(f"\nTotal profiles created: {created_count}")
    
    # Verify the results
    total_ojt_profiles = OjtUser.objects.count()
    completed_profiles = OjtUser.objects.filter(ojt_status='completed').count()
    
    print(f"Total OjtUser profiles: {total_ojt_profiles}")
    print(f"Completed OJT profiles: {completed_profiles}")
    
    print("=== OjtUser Profile Creation Complete ===")
    return {
        'created_count': created_count,
        'total_profiles': total_ojt_profiles,
        'completed_profiles': completed_profiles
    }

def ojt_statistics_view(request):
    """View for OJT statistics"""
    return render(request, 'ojt_stats/statistics.html')

def generate_ojt_statistics_view(request):
    """View for generating OJT statistics"""
    return JsonResponse({'message': 'OJT statistics generation endpoint'})


def export_detailed_ojt_data(request):
    """View for exporting detailed OJT data"""
     return JsonResponse({'message': 'OJT data export endpoint'})
