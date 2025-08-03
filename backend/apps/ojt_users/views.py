# Views for OJT users will be added here in the future.

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from apps.shared.models import User, Notification
from apps.ojt_users.models import OjtUser
import json

@csrf_exempt
@require_http_methods(["GET"])
def debug_admin_users(request):
    """
    Debug view to check admin users
    """
    admin_users = User.objects.filter(account_type__admin=True)
    admin_list = []
    for user in admin_users:
        admin_list.append({
            'username': user.acc_username,
            'name': f"{user.f_name} {user.l_name}",
            'account_type_id': user.account_type.account_type_id,
            'admin': user.account_type.admin,
            'user': user.account_type.user,
            'coordinator': user.account_type.coordinator
        })
    
    return JsonResponse({
        'success': True,
        'admin_users_count': admin_users.count(),
        'admin_users': admin_list
    })

@csrf_exempt
@require_http_methods(["POST"])
def send_ojt_completed_notification_to_admin(request):
    """
    Send notification to admin when OJT completed records are sent to admin
    """
    try:
        data = json.loads(request.body)
        batch_year = data.get('batch_year')
        course = data.get('course', '')
        coordinator_username = data.get('coordinator_username', '')
        
        # Get all admin users
        admin_users = User.objects.filter(account_type__admin=True)
        
        # Get completed OJT records
        ojt_users = User.objects.filter(account_type__ojt=True)
        
        if batch_year:
            ojt_users = ojt_users.filter(year_graduated=batch_year)
        if course:
            ojt_users = ojt_users.filter(course=course)
        
        completed_records = []
        for user in ojt_users:
            try:
                ojt_profile = user.ojt_profile
                if ojt_profile.ojt_status == 'completed':
                                    completed_records.append({
                    'name': f"{user.f_name} {user.l_name}",
                    'ctu_id': user.acc_username,
                    'first_name': user.f_name or 'N/A',
                    'middle_name': user.m_name or 'N/A',
                    'last_name': user.l_name or 'N/A',
                    'gender': user.gender or 'N/A',
                    'birthdate': user.birthdate.strftime('%m/%d/%Y') if user.birthdate else 'N/A',
                    'phone': user.phone_num or 'N/A',
                    'address': user.address or 'N/A',
                    'social_media': user.social_media or 'N/A',
                    'civil_status': user.civil_status or 'N/A',
                    'age': user.age or 'N/A'
                })
            except:
                continue
        
        if not completed_records:
            return JsonResponse({
                'success': False,
                'message': 'No completed OJT records found'
            })
        
        # Create notification content
        notification_content = f"""
OJT Completed Records Sent to Admin

Batch Year: {batch_year or 'All'}
Course: {course or 'All'}
Coordinator: {coordinator_username or 'System'}

Completed Records ({len(completed_records)}):
"""
        
        for i, record in enumerate(completed_records, 1):
            notification_content += f"""
{i}. {record['name']}
   CTU_ID: {record['ctu_id']}
   First Name: {record['first_name']}
   Middle Name: {record['middle_name']}
   Last Name: {record['last_name']}
   Gender: {record['gender']}
   Birthdate: {record['birthdate']}
   Phone Number: {record['phone']}
   Address: {record['address']}
   Social Media: {record['social_media']}
   Civil Status: {record['civil_status']}
   Age: {record['age']}
"""
        
        notification_content += f"""

Total completed records sent: {len(completed_records)}
Date: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Send notification to all admin users
        notifications_created = 0
        for admin_user in admin_users:
            try:
                Notification.objects.create(
                    user=admin_user,
                    notif_type='OJT_COMPLETED',
                    subject='OJT Completed Records Sent to Admin',
                    notifi_content=notification_content,
                    notif_date=timezone.now()
                )
                notifications_created += 1
            except Exception as e:
                print(f"Error creating notification for admin {admin_user.acc_username}: {e}")
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully sent notifications to {notifications_created} admin users',
            'records_count': len(completed_records),
            'notifications_sent': notifications_created
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error sending notifications: {str(e)}'
        })
