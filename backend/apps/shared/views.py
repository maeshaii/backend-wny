from django.shortcuts import render
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
from io import BytesIO
import logging

# Create your views here.

# Export alumni data to Excel

def export_alumni_excel(request):
    batch_year = request.GET.get('batch_year')
    alumni = User.objects.filter(account_type__user=True)
    if batch_year:
        alumni = alumni.filter(year_graduated=batch_year)
    data = []
    for alum in alumni:
        data.append({
            "CTU_ID": alum.acc_username,
            "First_Name": alum.f_name,
            "Middle_Name": alum.m_name,
            "Last_Name": alum.l_name,
            "Gender": alum.gender,
            "Birthdate": getattr(alum, 'birthdate', ''),
            "Phone_Number": alum.phone_num,
            "Address": alum.address,
            "Social_Media": getattr(alum, 'social_media', ''),
            "Civil_Status": getattr(alum, 'civil_status', ''),
            "Age": getattr(alum, 'age', ''),
            "Email": getattr(alum, 'email', ''),
            "Program_Name": getattr(alum, 'program', '') or getattr(alum, 'course', ''),
            "Status": getattr(alum, 'status', '') or getattr(alum, 'user_status', ''),
            "Company name current": getattr(alum, 'company_name_current', ''),
            "Position current": getattr(alum, 'position_current', ''),
            "Sector current": getattr(alum, 'sector_current', ''),
            "Employment duration current": getattr(alum, 'employment_duration_current', ''),
            "Salary current": getattr(alum, 'salary_current', ''),
            "Supporting document current": getattr(alum, 'supporting_document_current', ''),
            "Awards recognition current": getattr(alum, 'awards_recognition_current', ''),
            "Supporting document awards recognition": getattr(alum, 'supporting_document_awards_recognition', ''),
            "Unemployment reason": getattr(alum, 'unemployment_reason', ''),
            "Pursue further study": getattr(alum, 'pursue_further_study', ''),
            "Date started": getattr(alum, 'date_started', ''),
            "School name": getattr(alum, 'school_name', ''),
        })
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=alumni_export.xlsx'
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
