from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from apps.shared.models import User
import json
from django.db import models

# List all OJT users with filtering options
@csrf_exempt
@require_http_methods(["GET"])
def list_ojt_users(request):
    """
    List OJT users with optional filtering by year, course, status, and search
    """
    try:
        # Get filter parameters
        year = request.GET.get('year')
        course = request.GET.get('course')
        status = request.GET.get('status')
        search = request.GET.get('search')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        # Start with all OJT users
        ojt_users = User.objects.filter(account_type__ojt=True)
        
        # Apply filters
        if year and year != 'ALL':
            ojt_users = ojt_users.filter(year_graduated=year)
        if course and course != 'ALL':
            ojt_users = ojt_users.filter(course=course)
        if status and status != 'ALL':
            ojt_users = ojt_users.filter(ojtstatus=status)
        if search:
            ojt_users = ojt_users.filter(
                Q(f_name__icontains=search) |
                Q(l_name__icontains=search) |
                Q(acc_username__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Get total count for pagination
        total_count = ojt_users.count()
        
        # Apply pagination
        start = (page - 1) * per_page
        end = start + per_page
        ojt_users = ojt_users[start:end]
        
        # Prepare user data
        users_data = []
        for user in ojt_users:
            users_data.append({
                'user_id': user.user_id,
                'username': user.acc_username,
                'first_name': user.f_name,
                'middle_name': user.m_name,
                'last_name': user.l_name,
                'email': user.email,
                'course': user.course,
                'section': user.section,
                'year_graduated': user.year_graduated,
                'ojt_status': user.ojtstatus,
                'ojt_start_date': user.date_started,
                'ojt_end_date': user.ojt_end_date,
                'phone_number': user.phone_num,
                'address': user.address,
                'gender': user.gender,
                'civil_status': user.civil_status,
                'birthdate': user.birthdate,
                'age': user.age,
            })
        
        return JsonResponse({
            'success': True,
            'users': users_data,
            'total_count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page,
            'filters': {
                'year': year,
                'course': course,
                'status': status,
                'search': search
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Get individual OJT user details
@csrf_exempt
@require_http_methods(["GET"])
def get_ojt_user_details(request, user_id):
    """
    Get detailed information for a specific OJT user
    """
    try:
        user = get_object_or_404(User, user_id=user_id, account_type__ojt=True)
        
        user_data = {
            'CTU_ID': user.user_id,
            'First_Name': user.f_name,
            'Middle_Name': user.m_name,
            'Last_Name': user.l_name,
            'Gender': user.gender,
            'Birthdate': user.birthdate,
            'Phone_Number': user.phone_num,
            'Social_Media': user.email,
            'Address': user.address,
            'Course': user.course,
            'Ojt_Start_Date': user.date_started,
            'Ojt_End_Date': user.ojt_end_date,
            'Status': user.ojtstatus,
            'Civil_Status': user.civil_status,
        }
        
        return JsonResponse({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Update OJT user status (for coordinators)
@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def update_ojt_status(request, user_id):
    """
    Update OJT status for a specific user (coordinator function)
    """
    try:
        user = get_object_or_404(User, user_id=user_id, account_type__ojt=True)
        
        # Parse request body
        data = json.loads(request.body)
        new_status = data.get('ojt_status')
        
        # Validate status
        valid_statuses = ['Ongoing', 'Completed', 'Incomplete']
        if new_status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }, status=400)
        
        # Update status
        user.ojtstatus = new_status
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': f'OJT status updated to {new_status}',
            'user_id': user_id,
            'new_status': new_status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Update OJT user information
@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def update_ojt_user(request, user_id):
    """
    Update OJT user information
    """
    try:
        user = get_object_or_404(User, user_id=user_id, account_type__ojt=True)
        
        # Parse request body
        data = json.loads(request.body)
        
        # Fields that can be updated
        updatable_fields = [
            'f_name', 'm_name', 'l_name', 'email', 'phone_num', 'address',
            'profile_bio', 'gender', 'birthdate', 'civil_status', 'social_media',
            'course', 'section', 'program', 'date_started', 'ojt_end_date',
            'school_name', 'job_code'
        ]
        
        # Update allowed fields
        updated_fields = []
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
                updated_fields.append(field)
        
        if updated_fields:
            user.save()
            return JsonResponse({
                'success': True,
                'message': f'Updated fields: {", ".join(updated_fields)}',
                'user_id': user_id,
                'updated_fields': updated_fields
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No valid fields to update'
            }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Create new OJT user
@csrf_exempt
@require_http_methods(["POST"])
def create_ojt_user(request):
    """
    Create a new OJT user
    """
    try:
        data = json.loads(request.body)
        
        # Required fields
        required_fields = ['acc_username', 'f_name', 'l_name', 'email', 'course']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # Check if username already exists
        if User.objects.filter(acc_username=data['acc_username']).exists():
            return JsonResponse({
                'success': False,
                'error': 'Username already exists'
            }, status=400)
        
        # Create user with OJT account type
        user = User.objects.create(
            acc_username=data['acc_username'],
            f_name=data['f_name'],
            m_name=data.get('m_name', ''),
            l_name=data['l_name'],
            email=data['email'],
            course=data['course'],
            section=data.get('section', ''),
            year_graduated=data.get('year_graduated'),
            phone_num=data.get('phone_num', ''),
            address=data.get('address', ''),
            gender=data.get('gender', ''),
            civil_status=data.get('civil_status', ''),
            birthdate=data.get('birthdate'),
            date_started=data.get('date_started'),
            ojt_end_date=data.get('ojt_end_date'),
            school_name=data.get('school_name', ''),
            job_code=data.get('job_code', ''),
            ojtstatus='Ongoing',  # Default status
            account_type_id=2,  # Assuming 2 is OJT account type
        )
        
        return JsonResponse({
            'success': True,
            'message': 'OJT user created successfully',
            'user_id': user.user_id,
            'username': user.acc_username
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Delete OJT user
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_ojt_user(request, user_id):
    """
    Delete an OJT user
    """
    try:
        user = get_object_or_404(User, user_id=user_id, account_type__ojt=True)
        
        # Soft delete by setting user_status to inactive
        user.user_status = 'Inactive'
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'OJT user deactivated successfully',
            'user_id': user_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Get OJT statistics summary
@csrf_exempt
@require_http_methods(["GET"])
def ojt_users_summary(request):
    """
    Get summary statistics for OJT users
    """
    try:
        # Get filter parameters
        year = request.GET.get('year')
        course = request.GET.get('course')
        
        # Start with all OJT users
        ojt_users = User.objects.filter(account_type__ojt=True)
        
        # Apply filters
        if year and year != 'ALL':
            ojt_users = ojt_users.filter(year_graduated=year)
        if course and course != 'ALL':
            ojt_users = ojt_users.filter(course=course)
        
        # Calculate statistics
        total_users = ojt_users.count()
        status_counts = ojt_users.values('ojtstatus').annotate(count=models.Count('ojtstatus'))
        course_counts = ojt_users.values('course').annotate(count=models.Count('course'))
        year_counts = ojt_users.values('year_graduated').annotate(count=models.Count('year_graduated'))
        
        return JsonResponse({
            'success': True,
            'summary': {
                'total_users': total_users,
                'status_breakdown': list(status_counts),
                'course_breakdown': list(course_counts),
                'year_breakdown': list(year_counts),
                'filters': {
                    'year': year,
                    'course': course
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
