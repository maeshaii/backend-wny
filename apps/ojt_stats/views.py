from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.shared.models import User, OJTImport
from collections import Counter
from django.db import models
from statistics import mean
from django.utils import timezone
from datetime import datetime, timedelta
import json

# Helper functions for statistics aggregation

def safe_mode(qs, field):
    vals = [getattr(a, field) for a in qs if getattr(a, field)]
    return Counter(vals).most_common(1)[0][0] if vals else None

def safe_mean(qs, field):
    vals = []
    for a in qs:
        v = getattr(a, field)
        if v and isinstance(v, (int, float)):
            vals.append(float(v))
        elif v and isinstance(v, str):
            try:
                vals.append(float(v.replace(',', '').replace(' ', '')))
            except:
                continue
    return round(mean(vals), 2) if vals else None

def safe_sample(qs, field):
    for a in qs:
        v = getattr(a, field)
        if v:
            return v
    return None

# Create your views here.

@csrf_exempt
@require_http_methods(["GET"])
def ojt_statistics_view(request):
    """
    Main OJT statistics view for coordinators to see overview of OJT statuses
    """
    year = request.GET.get('year')
    course = request.GET.get('course')
    ojt_qs = User.objects.filter(account_type__ojt=True)
    
    if year and year != 'ALL':
        ojt_qs = ojt_qs.filter(year_graduated=year)
    if course and course != 'ALL':
        ojt_qs = ojt_qs.filter(course=course)
    
    # Count by OJT status (Ongoing, Completed, Incomplete)
    status_counts = Counter(ojt_qs.values_list('ojtstatus', flat=True))
    
    # Count by year for year options
    year_counts = Counter(User.objects.filter(account_type__ojt=True).values_list('year_graduated', flat=True))
    filtered_year_counts = {y: c for y, c in year_counts.items() if y is not None}
    
    # Calculate completion rates
    total_ojt = ojt_qs.count()
    completed_count = status_counts.get('Completed', 0)
    ongoing_count = status_counts.get('Ongoing', 0)
    incomplete_count = status_counts.get('Incomplete', 0)
    
    completion_rate = round((completed_count / total_ojt * 100), 2) if total_ojt > 0 else 0
    ongoing_rate = round((ongoing_count / total_ojt * 100), 2) if total_ojt > 0 else 0
    incomplete_rate = round((incomplete_count / total_ojt * 100), 2) if total_ojt > 0 else 0
    
    return JsonResponse({
        'success': True,
        'total_ojt': total_ojt,
        'status_counts': dict(status_counts),
        'completion_rate': completion_rate,
        'ongoing_rate': ongoing_rate,
        'incomplete_rate': incomplete_rate,
        'years': [
            {'year': year, 'count': count}
            for year, count in sorted(filtered_year_counts.items(), reverse=True)
        ]
    })

@csrf_exempt
@require_http_methods(["GET"])
def generate_ojt_statistics_view(request):
    """
    Detailed OJT statistics view for coordinators to analyze different aspects
    """
    year = request.GET.get('year', 'ALL')
    course = request.GET.get('course', 'ALL')
    stats_type = request.GET.get('type', 'ALL')
    
    ojt_qs = User.objects.filter(account_type__ojt=True)
    
    if year and year != 'ALL':
        ojt_qs = ojt_qs.filter(year_graduated=year)
    if course and course != 'ALL':
        ojt_qs = ojt_qs.filter(course=course)
    
    total_ojt = ojt_qs.count()
    
    if stats_type == 'ALL':
        # Return comprehensive OJT status statistics
        status_counts = Counter(ojt_qs.values_list('ojtstatus', flat=True))
        
        # Calculate rates for each status
        completed_rate = round((status_counts.get('Completed', 0) / total_ojt * 100), 2) if total_ojt > 0 else 0
        ongoing_rate = round((status_counts.get('Ongoing', 0) / total_ojt * 100), 2) if total_ojt > 0 else 0
        incomplete_rate = round((status_counts.get('Incomplete', 0) / total_ojt * 100), 2) if total_ojt > 0 else 0
        
        return JsonResponse({
            'success': True,
            'type': 'ALL',
            'total_ojt': total_ojt,
            'status_counts': dict(status_counts),
            'completion_rate': completed_rate,
            'ongoing_rate': ongoing_rate,
            'incomplete_rate': incomplete_rate,
            'most_common_course': safe_mode(ojt_qs, 'course'),
            'most_common_section': safe_mode(ojt_qs, 'section'),
            'most_common_gender': safe_mode(ojt_qs, 'gender'),
            'most_common_civil_status': safe_mode(ojt_qs, 'civil_status'),
            'average_age': safe_mean(ojt_qs, 'age'),
            'year': year,
            'course': course
        })
    
    elif stats_type == 'status_tracking':
        # Focus on OJT status tracking and progression
        status_counts = Counter(ojt_qs.values_list('ojtstatus', flat=True))
        
        # Get students by status for detailed analysis
        completed_students = ojt_qs.filter(ojtstatus='Completed')
        ongoing_students = ojt_qs.filter(ojtstatus='Ongoing')
        incomplete_students = ojt_qs.filter(ojtstatus='Incomplete')
        
        return JsonResponse({
            'success': True,
            'type': 'status_tracking',
            'total_ojt': total_ojt,
            'status_counts': dict(status_counts),
            'completed_students_count': completed_students.count(),
            'ongoing_students_count': ongoing_students.count(),
            'incomplete_students_count': incomplete_students.count(),
            'completion_rate': round((completed_students.count() / total_ojt * 100), 2) if total_ojt > 0 else 0,
            'ongoing_rate': round((ongoing_students.count() / total_ojt * 100), 2) if total_ojt > 0 else 0,
            'incomplete_rate': round((incomplete_students.count() / total_ojt * 100), 2) if total_ojt > 0 else 0,
            'year': year,
            'course': course
        })
    
    elif stats_type == 'academic_progress':
        # Academic progress statistics by OJT status
        completed_students = ojt_qs.filter(ojtstatus='Completed')
        ongoing_students = ojt_qs.filter(ojtstatus='Ongoing')
        incomplete_students = ojt_qs.filter(ojtstatus='Incomplete')
        
        return JsonResponse({
            'success': True,
            'type': 'academic_progress',
            'total_ojt': total_ojt,
            'completed': {
                'count': completed_students.count(),
                'most_common_course': safe_mode(completed_students, 'course'),
                'most_common_section': safe_mode(completed_students, 'section'),
                'most_common_school': safe_mode(completed_students, 'school_name'),
            },
            'ongoing': {
                'count': ongoing_students.count(),
                'most_common_course': safe_mode(ongoing_students, 'course'),
                'most_common_section': safe_mode(ongoing_students, 'section'),
                'most_common_school': safe_mode(ongoing_students, 'school_name'),
            },
            'incomplete': {
                'count': incomplete_students.count(),
                'most_common_course': safe_mode(incomplete_students, 'course'),
                'most_common_section': safe_mode(incomplete_students, 'section'),
                'most_common_school': safe_mode(incomplete_students, 'school_name'),
            },
            'year': year,
            'course': course
        })
    
    elif stats_type == 'coordinator_summary':
        # Summary view for coordinators to see their OJT management overview
        status_counts = Counter(ojt_qs.values_list('ojtstatus', flat=True))
        
        # Calculate key metrics for coordinators
        total_completed = status_counts.get('Completed', 0)
        total_ongoing = status_counts.get('Ongoing', 0)
        total_incomplete = status_counts.get('Incomplete', 0)
        
        return JsonResponse({
            'success': True,
            'type': 'coordinator_summary',
            'total_ojt': total_ojt,
            'status_summary': {
                'completed': {
                    'count': total_completed,
                    'percentage': round((total_completed / total_ojt * 100), 2) if total_ojt > 0 else 0
                },
                'ongoing': {
                    'count': total_ongoing,
                    'percentage': round((total_ongoing / total_ojt * 100), 2) if total_ojt > 0 else 0
                },
                'incomplete': {
                    'count': total_incomplete,
                    'percentage': round((total_incomplete / total_ojt * 100), 2) if total_ojt > 0 else 0
                }
            },
            'most_common_course': safe_mode(ojt_qs, 'course'),
            'year': year,
            'course': course
        })
    
    else:
        return JsonResponse({
            'success': False,
            'error': 'Invalid statistics type. Use: ALL, status_tracking, academic_progress, or coordinator_summary'
        })

@csrf_exempt
@require_http_methods(["GET"])
def export_detailed_ojt_data(request):
    """
    Export detailed OJT data for coordinators to analyze and report
    """
    year = request.GET.get('year', 'ALL')
    course = request.GET.get('course', 'ALL')
    status_filter = request.GET.get('status', 'ALL')  # Filter by specific OJT status
    
    ojt_qs = User.objects.filter(account_type__ojt=True)
    
    if year and year != 'ALL':
        ojt_qs = ojt_qs.filter(year_graduated=year)
    if course and course != 'ALL':
        ojt_qs = ojt_qs.filter(course=course)
    if status_filter and status_filter != 'ALL':
        ojt_qs = ojt_qs.filter(ojtstatus=status_filter)
    
    # Prepare data for export
    export_data = []
    
    for ojt_user in ojt_qs:
        user_data = {
            'CTU_ID': ojt_user.user_id,
            'First_Name': ojt_user.f_name,
            'Middle_Name': ojt_user.m_name,
            'Last_Name': ojt_user.l_name,
            'Gender': ojt_user.gender,
            'Birthdate': ojt_user.birthdate,
            'Phone_Number': ojt_user.phone_num,
            'Social_Media': ojt_user.email,
            'Address': ojt_user.address,
            'Course': ojt_user.course,
            'Ojt_Start_Date': ojt_user.date_started,
            'Ojt_End_Date': ojt_user.ojt_end_date,
            'Status': ojt_user.ojtstatus,
            'Civil_Status': ojt_user.civil_status,
        }
        export_data.append(user_data)
    
    return JsonResponse({
        'success': True,
        'data': export_data,
        'total_records': len(export_data),
        'year': year,
        'course': course,
        'status_filter': status_filter,
        'export_date': timezone.now().isoformat()
    })
