from django.shortcuts import render
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import User, TrackerResponse, Question, Notification
from io import BytesIO
import logging

# Create your views here.

# Export alumni data to Excel

def export_alumni_excel(request):
    batch_year = request.GET.get('batch_year')
    alumni = User.objects.filter(account_type__user=True)
    if batch_year:
        alumni = alumni.filter(year_graduated=batch_year)

    # Basic User model fields to always include
    basic_fields = [
        ("CTU_ID", "acc_username"),
        ("First Name", "f_name"),
        ("Middle Name", "m_name"),
        ("Last Name", "l_name"),
        ("Gender", "gender"),
        ("Birthdate", "birthdate"),
        ("Phone Number", "phone_num"),
        ("Address", "address"),
        ("Social Media", "social_media"),
        ("Civil Status", "civil_status"),
        ("Age", "age"),
        ("Email", "email"),
        ("Program Name", "program"),
        
    ]

    # Collect all tracker question texts that have been answered by any alumni
    all_tracker_qids = set()
    for alum in alumni:
        tracker_responses = TrackerResponse.objects.filter(user=alum).order_by('-submitted_at')
        latest_tracker = tracker_responses.first() if tracker_responses.exists() else None
        tracker_answers = latest_tracker.answers if latest_tracker and latest_tracker.answers else {}
        all_tracker_qids.update([int(qid) for qid in tracker_answers.keys() if str(qid).isdigit()])
    # Get question text for all qids
    tracker_questions = {q.id: q.text for q in Question.objects.filter(id__in=all_tracker_qids)}
    tracker_columns = [tracker_questions[qid] for qid in sorted(tracker_questions.keys())]

    # Build a unique set of export columns: basic fields + tracker question texts (no duplicates)
    export_columns = []
    seen = set()
    for col, _ in basic_fields:
        if col not in seen:
            export_columns.append(col)
            seen.add(col)
    for qtext in tracker_columns:
        if qtext not in seen:
            export_columns.append(qtext)
            seen.add(qtext)

    data = []
    for alum in alumni:
        row = {}
        # Fill basic fields
        for col, field in basic_fields:
            value = getattr(alum, field, "")
            row[col] = value if value is not None else ""
        # Fill tracker answers, but only if not already filled by user model
        tracker_responses = TrackerResponse.objects.filter(user=alum).order_by('-submitted_at')
        latest_tracker = tracker_responses.first() if tracker_responses.exists() else None
        tracker_answers = latest_tracker.answers if latest_tracker and latest_tracker.answers else {}
        for qid, qtext in tracker_questions.items():
            if qtext in row and row[qtext]:
                continue  # Already filled by user model
            answer = tracker_answers.get(str(qid)) or tracker_answers.get(qid)
            if isinstance(answer, list):
                answer = ', '.join(str(a) for a in answer)
            row[qtext] = answer if answer is not None else ""
        data.append(row)
    df = pd.DataFrame(data, columns=export_columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=alumni_export.xlsx'
    return response

# Export OJT data with completed status to Excel
def export_ojt_completed_excel(request):
    batch_year = request.GET.get('batch_year')
    course = request.GET.get('course', '')
    coordinator_username = request.GET.get('coordinator_username', '')
    
    # Filter OJT users with completed status
    ojt_users = User.objects.filter(account_type__ojt=True)
    
    if batch_year:
        ojt_users = ojt_users.filter(year_graduated=batch_year)
    if course:
        ojt_users = ojt_users.filter(course=course)
    
    # Basic fields to include (only basic info, no OJT details)
    basic_fields = [
        ("CTU_ID", "acc_username"),
        ("First Name", "f_name"),
        ("Middle Name", "m_name"),
        ("Last Name", "l_name"),
        ("Gender", "gender"),
        ("Birthdate", "birthdate"),
        ("Phone Number", "phone_num"),
        ("Address", "address"),
        ("Social Media", "social_media"),
        ("Civil Status", "civil_status"),
        ("Age", "age"),
    ]

    # Get basic data from User model (no OJT details)
    ojt_data = []
    for user in ojt_users:
        try:
            ojt_profile = user.ojt_profile
            # Only include if status is completed
            if ojt_profile.ojt_status == 'completed':
                row = {}
                # Fill basic fields only
                for col, field in basic_fields:
                    value = getattr(user, field, "")
                    row[col] = value if value is not None else ""
                
                ojt_data.append(row)
        except:
            # Skip if no OJT profile exists
            continue

    # Create DataFrame with basic columns only
    all_columns = [col for col, _ in basic_fields]
    
    df = pd.DataFrame(ojt_data, columns=all_columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    
    filename = f"ojt_completed_export"
    if batch_year:
        filename += f"_batch_{batch_year}"
    if course:
        filename += f"_{course}"
    filename += ".xlsx"
    
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response

# Export OJT data with completed status to Excel and remove extract file
def export_ojt_completed_and_remove_extract(request):
    batch_year = request.GET.get('batch_year')
    course = request.GET.get('course', '')
    coordinator_username = request.GET.get('coordinator_username', '')
    
    # Filter OJT users with completed status
    ojt_users = User.objects.filter(account_type__ojt=True)
    
    if batch_year:
        ojt_users = ojt_users.filter(year_graduated=batch_year)
    if course:
        ojt_users = ojt_users.filter(course=course)
    
    # Basic fields to include (only basic info, no OJT details)
    basic_fields = [
        ("CTU_ID", "acc_username"),
        ("First Name", "f_name"),
        ("Middle Name", "m_name"),
        ("Last Name", "l_name"),
        ("Gender", "gender"),
        ("Birthdate", "birthdate"),
        ("Phone Number", "phone_num"),
        ("Address", "address"),
        ("Social Media", "social_media"),
        ("Civil Status", "civil_status"),
        ("Age", "age"),
    ]

    # Get basic data from User model (no OJT details)
    ojt_data = []
    for user in ojt_users:
        try:
            ojt_profile = user.ojt_profile
            # Only include if status is completed
            if ojt_profile.ojt_status == 'completed':
                row = {}
                # Fill basic fields only
                for col, field in basic_fields:
                    value = getattr(user, field, "")
                    row[col] = value if value is not None else ""
                
                ojt_data.append(row)
        except:
            # Skip if no OJT profile exists
            continue

    # Create DataFrame with basic columns only
    all_columns = [col for col, _ in basic_fields]
    
    df = pd.DataFrame(ojt_data, columns=all_columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    
    filename = f"ojt_completed_export"
    if batch_year:
        filename += f"_batch_{batch_year}"
    if course:
        filename += f"_{course}"
    filename += ".xlsx"
    
    # After exporting, remove the extract file by updating OJT status
    # This will mark the records as "sent to admin" and remove them from the extract
    completed_records = []
    for user in ojt_users:
        try:
            ojt_profile = user.ojt_profile
            if ojt_profile.ojt_status == 'completed':
                # Store record info for notification
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
                # Update status to indicate it's been sent to admin
                ojt_profile.ojt_status = 'sent_to_admin'
                ojt_profile.save()
        except:
            continue
    
    # Send notification to admin users
    if completed_records:
        admin_users = User.objects.filter(account_type__admin=True)
        print(f"Found {admin_users.count()} admin users")
        print(f"Completed records: {len(completed_records)}")
        
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
                print(f"Created notification for admin: {admin_user.acc_username}")
            except Exception as e:
                print(f"Error creating notification for admin {admin_user.acc_username}: {e}")
                continue
        
        print(f"Total notifications created: {notifications_created}")
    
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response

# Import alumni data from Excel, updating only missing fields
@csrf_exempt
def import_alumni_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        batch_year = request.POST.get('batch_year')
        if not batch_year:
            return JsonResponse({'success': False, 'message': 'Batch year is required'}, status=400)
        df = pd.read_excel(request.FILES['file'])
        for _, row in df.iterrows():
            ctu_id = row.get('CTU_ID')
            if not ctu_id:
                continue
            # Try to find user by CTU ID and batch year
            user = User.objects.filter(acc_username=ctu_id, year_graduated=batch_year).first()
            field_map = {
                'First_Name': 'f_name',
                'Middle_Name': 'm_name',
                'Last_Name': 'l_name',
                'Gender': 'gender',
                'Phone_Number': 'phone_num',
                'Address': 'address',
                'Social Media Acc Link': 'social_media',
                'Civil Status': 'civil_status',
                'Company name current': 'company_name_current',
                'salary current': 'salary_current',
                'Post Graduate Degree': 'post_graduate_degree',
                # Add more mappings as needed
            }
            if user:
                # Only update fields that are empty in DB and present in Excel
                for excel_col, model_field in field_map.items():
                    excel_value = row.get(excel_col)
                    if excel_value and (not hasattr(user, model_field) or not getattr(user, model_field) or getattr(user, model_field) == ''):
                        setattr(user, model_field, excel_value)
                user.save()
            else:
                # Create new user for this batch
                user_data = {
                    'acc_username': ctu_id,
                    'year_graduated': batch_year,
                    # Set all fields from Excel if present
                }
                for excel_col, model_field in field_map.items():
                    excel_value = row.get(excel_col)
                    if excel_value:
                        user_data[model_field] = excel_value
                user_data['account_type_id'] = 1  # Default to alumni account type
                User.objects.create(**user_data)
        return JsonResponse({'success': True, 'message': 'Import complete'})
    return JsonResponse({'success': False, 'message': 'No file uploaded'}, status=400)

@csrf_exempt
def import_exported_alumni_excel(request):
    logger = logging.getLogger(__name__)
    debug_info = []
    if request.method == 'POST' and request.FILES.get('file'):
        batch_year = request.POST.get('batch_year')
        if not batch_year:
            return JsonResponse({'success': False, 'message': 'Batch year is required'}, status=400)
        df = pd.read_excel(request.FILES['file'])
        for idx, row in df.iterrows():
            ctu_id = row.get('CTU_ID')
            if not ctu_id:
                debug_info.append(f'Row {idx+2}: Missing CTU_ID, skipped.')
                continue
            user = User.objects.filter(acc_username=ctu_id, year_graduated=batch_year).first()
            field_map = {
                'First_Name': 'f_name',
                'Middle_Name': 'm_name',
                'Last_Name': 'l_name',
                'Gender': 'gender',
                'Phone_Number': 'phone_num',
                'Address': 'address',
                'Social_Media': 'social_media',
                'Civil_Status': 'civil_status',
                'Age': 'age',
                'Email': 'email',
                'Program_Name': 'program',
                'Status': 'status',
                'Company name current': 'company_name_current',
                'Position current': 'position_current',
                'Sector current': 'sector_current',
                'Employment duration current': 'employment_duration_current',
                'Salary current': 'salary_current',
                'Supporting document current': 'supporting_document_current',
                'Awards recognition current': 'awards_recognition_current',
                'Supporting document awards recognition': 'supporting_document_awards_recognition',
                'Unemployment reason': 'unemployment_reason',
                'Pursue further study': 'pursue_further_study',
                'Date started': 'date_started',
                'School name': 'school_name',
                'Birthdate': 'birthdate',
            }
            updated_fields = []
            try:
                if user:
                    for excel_col, model_field in field_map.items():
                        excel_value = row.get(excel_col)
                        if excel_value and (not hasattr(user, model_field) or not getattr(user, model_field) or getattr(user, model_field) == ''):
                            setattr(user, model_field, excel_value)
                            updated_fields.append(model_field)
                    user.save()
                    debug_info.append(f'Row {idx+2}: Updated user {ctu_id} (fields: {", ".join(updated_fields) if updated_fields else "none"})')
                else:
                    user_data = {'acc_username': ctu_id, 'year_graduated': batch_year}
                    for excel_col, model_field in field_map.items():
                        excel_value = row.get(excel_col)
                        if excel_value:
                            user_data[model_field] = excel_value
                    user_data['account_type_id'] = 1
                    User.objects.create(**user_data)
                    debug_info.append(f'Row {idx+2}: Created new user {ctu_id}')
            except Exception as e:
                debug_info.append(f'Row {idx+2}: Error for CTU_ID {ctu_id}: {str(e)}')
        return JsonResponse({'success': True, 'message': 'Import complete', 'debug': debug_info})
    return JsonResponse({'success': False, 'message': 'No file uploaded'}, status=400)
