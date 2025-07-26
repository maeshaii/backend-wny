from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date
from apps.shared.models import User, AccountType, QuestionCategory, TrackerResponse, OJTImport
import json
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken
import pandas as pd
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from collections import Counter
from apps.shared.models import Question
from django.core.mail import send_mail
from django.utils import timezone
from apps.shared.models import Notification, User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'success': True, 'message': 'CSRF cookie set'})

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def login_view(request):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        return response

    try:
        data = json.loads(request.body)
        acc_username = data.get('acc_username')
        acc_password = data.get('acc_password')  # Expected: birthdate in 'YYYY-MM-DD' or 'MM/DD/YYYY'

        if not acc_username or not acc_password:
            return JsonResponse({'success': False, 'message': 'Missing credentials'}, status=400)

        # Accept MM/DD/YYYY or YYYY-MM-DD
        try:
            birthdate = datetime.strptime(acc_password, "%m/%d/%Y").date()
        except ValueError:
            birthdate = parse_date(acc_password)

        if not birthdate:
            return JsonResponse({'success': False, 'message': 'Invalid birthdate format'}, status=400)

        try:
            user = User.objects.get(acc_username=acc_username, acc_password=birthdate)  # type: ignore[attr-defined]
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.user_id,
                    'name': f"{user.f_name} {user.l_name}",
                    'year_graduated': user.year_graduated,
                    'account_type': {
                        'admin': user.account_type.admin,
                        'peso': user.account_type.peso,
                        'user': user.account_type.user,
                        'coordinator': user.account_type.coordinator,
                        'ojt': user.account_type.ojt,
                    }
                }
            })
        except User.DoesNotExist:  # type: ignore[attr-defined]
            return JsonResponse({'success': False, 'message': 'Invalid CTU ID or birthdate'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

class CustomTokenObtainPairSerializer(serializers.Serializer):
    acc_username = serializers.CharField()
    acc_password = serializers.CharField()

    def validate(self, attrs):
        print('DEBUG: Received attrs:', attrs)
        acc_username = attrs.get('acc_username')
        acc_password = attrs.get('acc_password')
        print('DEBUG: acc_username:', acc_username)
        print('DEBUG: acc_password:', acc_password)
        from django.utils.dateparse import parse_date
        from datetime import datetime
        if acc_password is None:
            print('DEBUG: acc_password is None')
            raise serializers.ValidationError('Password is required')
        try:
            birthdate = datetime.strptime(acc_password, "%m/%d/%Y").date()
            print('DEBUG: Parsed birthdate (MM/DD/YYYY):', birthdate)
        except ValueError:
            birthdate = parse_date(acc_password)
            print('DEBUG: Parsed birthdate (YYYY-MM-DD):', birthdate)
        if not birthdate:
            print('DEBUG: birthdate parsing failed')
            raise serializers.ValidationError('Invalid birthdate format')
        try:
            user = User.objects.get(acc_username=acc_username, acc_password=birthdate)  # type: ignore[attr-defined]
            print('DEBUG: Found user:', user)
        except User.DoesNotExist:  # type: ignore[attr-defined]
            print('DEBUG: User not found with acc_username and birthdate')
            raise serializers.ValidationError('Invalid credentials')
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
            'id': user.user_id,
            'name': f"{user.f_name} {user.l_name}",
            'year_graduated': user.year_graduated,
                'account_type': {
                    'admin': user.account_type.admin,
                    'peso': user.account_type.peso,
                    'user': user.account_type.user,
                    'coordinator': user.account_type.coordinator,
                    'ojt': user.account_type.ojt,
                }
            }
        }
        print('DEBUG: Returning data:', data)
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def import_alumni_view(request):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        return response

    try:
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No file uploaded'}, status=400)
        file = request.FILES['file']
        batch_year = request.POST.get('batch_year', '')
        course = request.POST.get('course', '')
        if not file.name.endswith(('.xlsx', '.xls')):
            return JsonResponse({'success': False, 'message': 'Please upload an Excel file (.xlsx or .xls)'}, status=400)
        if not batch_year or not course:
            return JsonResponse({'success': False, 'message': 'Batch year and course are required'}, status=400)
        # Read Excel file
        try:
            # Read without parse_dates first to see raw data
            df = pd.read_excel(file)
            print('HEADERS:', list(df.columns))
            print('DEBUG: Raw birthdate column first 5 rows:')
            print(df['Birthdate'].head())
            print('DEBUG: Birthdate column data types:', df['Birthdate'].dtype)
            
            # Now try to convert birthdate column to proper dates
            try:
                df['Birthdate'] = pd.to_datetime(df['Birthdate'], errors='coerce')
                print('DEBUG: After pd.to_datetime conversion:')
                print(df['Birthdate'].head())
            except Exception as e:
                print(f"DEBUG: Error converting dates: {e}")
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error reading Excel file: {str(e)}'}, status=400)
        required_columns = ['CTU_ID', 'First_Name', 'Last_Name', 'Gender', 'Birthdate']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JsonResponse({
                'success': False,
                'message': f'Missing required columns: {", ".join(missing_columns)}'
            }, status=400)
        # Get alumni account type (user=True)
        try:
            alumni_account_type = AccountType.objects.get(user=True, admin=False, peso=False, coordinator=False)
        except Exception:
            return JsonResponse({'success': False, 'message': 'Alumni account type not found'}, status=500)
        created_count = 0
        skipped_count = 0
        errors = []
        for index, row in df.iterrows():
            try:
                ctu_id = str(row['CTU_ID']).strip()
                first_name = str(row['First_Name']).strip()
                middle_name = str(row.get('Middle_Name', '')).strip() if pd.notna(row.get('Middle_Name')) else ''
                last_name = str(row['Last_Name']).strip()
                gender = str(row['Gender']).strip().upper()
                birthdate_str = str(row['Birthdate'])
                
                print(f"DEBUG: Row {index + 2} - CTU_ID: {ctu_id}, Name: {first_name} {last_name}")
                phone_number = str(row.get('Phone_Number', '')).strip() if pd.notna(row.get('Phone_Number')) else ''
                address = str(row.get('Address', '')).strip() if pd.notna(row.get('Address')) else ''
                civil_status = str(row.get('Civil Status', '')).strip() if pd.notna(row.get('Civil Status', '')) else ''
                social_media = str(row.get('Social Media', '')).strip() if pd.notna(row.get('Social Media', '')) else ''
                # Validate required fields
                if not ctu_id or not first_name or not last_name or not gender or not birthdate_str:
                    errors.append(f"Row {index + 2}: Missing required fields (CTU_ID, First_Name, Last_Name, Gender, Birthdate)")
                    continue
                # Validate gender
                if gender not in ['M', 'F']:
                    errors.append(f"Row {index + 2}: Gender must be 'M' or 'F'")
                    continue
                # SIMPLE BULLETPROOF BIRTHDATE PARSING
                print(f"DEBUG: Row {index + 2} - Raw birthdate: {row['Birthdate']} (type: {type(row['Birthdate'])})")
                
                birthdate = None
                
                # Method 1: Direct pandas datetime extraction
                try:
                    if pd.notna(row['Birthdate']):
                        if hasattr(row['Birthdate'], 'date'):
                            birthdate = row['Birthdate'].date()
                            print(f"DEBUG: Method 1 SUCCESS - Direct date extraction: {birthdate}")
                        elif hasattr(row['Birthdate'], 'to_pydatetime'):
                            birthdate = row['Birthdate'].to_pydatetime().date()
                            print(f"DEBUG: Method 1 SUCCESS - Pandas to datetime: {birthdate}")
                except Exception as e:
                    print(f"DEBUG: Method 1 failed: {e}")
                
                # Method 2: String parsing with ALL possible formats
                if not birthdate:
                    birthdate_str = str(row['Birthdate']).strip()
                    print(f"DEBUG: Trying string parsing with: '{birthdate_str}'")
                    
                    # Try every possible date format
                    formats_to_try = [
                        "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y",
                        "%Y/%m/%d", "%m/%d/%y", "%d/%m/%y", "%Y-%m-%d %H:%M:%S",
                        "%m/%d/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M",
                        "%m/%d/%Y %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S.%f",
                        "%m/%d/%Y %H:%M:%S.%f", "%d/%m/%Y %H:%M:%S.%f"
                    ]
                    
                    for fmt in formats_to_try:
                        try:
                            birthdate = datetime.strptime(birthdate_str, fmt).date()
                            print(f"DEBUG: Method 2 SUCCESS - String format '{fmt}': {birthdate}")
                            break
                        except ValueError:
                            continue
                
                # Method 3: Force pandas conversion
                if not birthdate:
                    try:
                        pd_date = pd.to_datetime(row['Birthdate'], errors='coerce', infer_datetime_format=True)
                        if pd.notna(pd_date):
                            birthdate = pd_date.date()
                            print(f"DEBUG: Method 3 SUCCESS - Pandas force conversion: {birthdate}")
                    except Exception as e:
                        print(f"DEBUG: Method 3 failed: {e}")
                
                # Method 4: Excel date number conversion
                if not birthdate:
                    try:
                        if isinstance(row['Birthdate'], (int, float)):
                            # Excel stores dates as numbers (days since 1900-01-01)
                            excel_date = row['Birthdate']
                            if excel_date > 1:  # Valid Excel date
                                from datetime import timedelta
                                excel_epoch = datetime(1900, 1, 1)
                                birthdate = excel_epoch + timedelta(days=int(excel_date) - 2)  # -2 for Excel's leap year bug
                                print(f"DEBUG: Method 4 SUCCESS - Excel date number {excel_date} -> {birthdate}")
                    except Exception as e:
                        print(f"DEBUG: Method 4 failed: {e}")
                
                if not birthdate:
                    print(f"DEBUG: ALL METHODS FAILED for birthdate: {row['Birthdate']}")
                    errors.append(f"Row {index + 2}: Cannot parse birthdate '{row['Birthdate']}'. Please check the format.")
                    continue
                else:
                    print(f"DEBUG: FINAL SUCCESS - Birthdate saved as: {birthdate}")
                # Check if user already exists
                if User.objects.filter(acc_username=ctu_id).exists():
                    errors.append(f"Row {index + 2}: CTU ID {ctu_id} already exists (skipped)")
                    skipped_count += 1
                    continue
                # Create user
                user = User.objects.create(
                    acc_username=ctu_id,
                    acc_password=birthdate,  # for login
                    birthdate=birthdate,     # for display and correct field
                    user_status='active',
                    f_name=first_name,
                    m_name=middle_name,
                    l_name=last_name,
                    gender=gender,
                    phone_num=phone_number if phone_number else None,
                    address=address if address else None,
                    year_graduated=int(batch_year) if batch_year.isdigit() else None,
                    course=course,
                    account_type=alumni_account_type,
                    civil_status=civil_status if civil_status else None,
                    social_media=social_media if social_media else None,
                )
                
                # Verify the birthdate was saved correctly
                saved_user = User.objects.get(user_id=user.user_id)
                print(f"DEBUG: VERIFICATION - User {ctu_id} birthdate saved as: {saved_user.acc_password}")
                
                created_count += 1
            except Exception as e:
                errors.append(f"Row {index + 2}: Unexpected error: {str(e)}")
                continue
        return JsonResponse({
            'success': True,
            'message': f'Successfully created {created_count} alumni accounts. Skipped {skipped_count} duplicates.',
            'created_count': created_count,
            'skipped_count': skipped_count,
            'errors': errors
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Server error: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def alumni_statistics_view(request):
    # Get all alumni users
    alumni = User.objects.filter(account_type__user=True)
    # Count by year_graduated
    year_counts = Counter(alumni.values_list('year_graduated', flat=True))
    # Optionally, add more breakdowns (by course, gender, etc.)
    return JsonResponse({
        'success': True,
        'years': [
            {'year': year, 'count': count}
            for year, count in sorted(year_counts.items(), reverse=True) if year is not None
        ]
    })

@csrf_exempt
@require_http_methods(["GET"])
def alumni_list_view(request):
    alumni = User.objects.filter(account_type__user=True)
    alumni_data = [
        {
            'id': a.user_id,
            'ctu_id': a.acc_username,
            'name': f"{a.f_name} {a.m_name or ''} {a.l_name}",
            'course': a.course,
            'batch': a.year_graduated,
            'status': a.user_status,
            'gender': a.gender,
            'birthdate': str(a.birthdate) if a.birthdate else None,
            'phone': a.phone_num,
            'address': a.address,
            'civilStatus': a.civil_status,
            'socialMedia': a.social_media,
        }
        for a in alumni
    ]
    return JsonResponse({'success': True, 'alumni': alumni_data})

@csrf_exempt
@require_http_methods(["POST"])
def send_reminder_view(request):
    import json
    data = json.loads(request.body)
    emails = data.get('emails', [])
    user_ids = data.get('user_ids', [])
    message = data.get('message', '')
    subject = data.get('subject', 'Tracker Form Reminder')
    # Try to get sender name from request.user if authenticated, else fallback
    sender = 'CCICT'  # Always use CCICT as sender for tracker form notifications
    if not (emails or user_ids) or not message:
        return JsonResponse({'success': False, 'message': 'Missing users or message'}, status=400)
    sent = 0
    # Send by user_ids if provided, else by emails
    users = list(User.objects.filter(user_id__in=user_ids)) if user_ids else list(User.objects.filter(email__in=emails))
    tracker_form_base_url = "https://yourdomain.com/tracker/fill"  # Change to your actual domain/path
    for user in users:
        try:
            personalized_message = message.replace('[User\'s Name]', f"{user.f_name} {user.l_name}")
            user_link = f"{tracker_form_base_url}?user={user.user_id}"
            personalized_message = personalized_message.replace('[Tracker Form Link]', user_link)
            Notification.objects.create(
                user=user,
                notif_type=sender,
                notifi_content=personalized_message,
                notif_date=timezone.now(),
                subject=subject
            )
            sent += 1
        except Exception as e:
            continue
    return JsonResponse({'success': True, 'sent': sent, 'total': len(users)})

@csrf_exempt
@require_http_methods(["GET"])
def notifications_view(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'user_id is required'}, status=400)
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    # Alumni: show all notifications; OJT: filter out tracker notifications
    if hasattr(user.account_type, 'user') and user.account_type.user:
        notifications = Notification.objects.filter(user_id=user_id).order_by('-notif_date')
    elif hasattr(user.account_type, 'ojt') and user.account_type.ojt:
        notifications = Notification.objects.filter(user_id=user_id).exclude(notif_type__iexact='tracker').order_by('-notif_date')
    else:
        notifications = Notification.objects.filter(user_id=user_id).exclude(notif_type__iexact='tracker').order_by('-notif_date')
    notif_list = [
        {
            'id': n.notification_id,
            'type': n.notif_type,
            'subject': getattr(n, 'subject', None) or 'Tracker Form Reminder',
            'content': n.notifi_content,
            'date': n.notif_date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for n in notifications
    ]
    return JsonResponse({'success': True, 'notifications': notif_list})

@csrf_exempt
@require_http_methods(["POST"])
def delete_notifications_view(request):
    import json
    try:
        data = json.loads(request.body)
        notif_ids = data.get('notification_ids', [])
        if not notif_ids:
            return JsonResponse({'success': False, 'message': 'No notification IDs provided'}, status=400)
        from apps.shared.models import Notification
        deleted, _ = Notification.objects.filter(notification_id__in=notif_ids).delete()
        return JsonResponse({'success': True, 'deleted': deleted})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    bio = request.data.get('bio')
    profile_pic = request.data.get('profile_pic')
    if bio is not None:
        user.profile_bio = bio
    if profile_pic is not None:
        user.profile_pic = profile_pic  # This should be a URL or handle file upload
    user.save()
    return Response({'success': True, 'bio': user.profile_bio, 'profile_pic': user.profile_pic}, status=status.HTTP_200_OK)
# OJT-specific import function for coordinators
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def import_ojt_view(request):
    print("IMPORT OJT VIEW CALLED")  # Debug print
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        return response

    try:
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No file uploaded'}, status=400)
        
        file = request.FILES['file']
        batch_year = request.POST.get('batch_year', '')
        course = request.POST.get('course', '')
        coordinator_username = request.POST.get('coordinator_username', '')
        
        if not file.name.endswith(('.xlsx', '.xls')):
            return JsonResponse({'success': False, 'message': 'Please upload an Excel file (.xlsx or .xls)'}, status=400)
        
        if not batch_year or not course or not coordinator_username:
            return JsonResponse({'success': False, 'message': 'Batch year, course, and coordinator username are required'}, status=400)
        
        # Read Excel file
        try:
            df = pd.read_excel(file)
            print('OJT IMPORT - HEADERS:', list(df.columns))
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error reading Excel file: {str(e)}'}, status=400)
        
        # OJT-specific required columns
        required_columns = ['CTU_ID', 'First_Name', 'Last_Name', 'Gender', 'Birthdate']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JsonResponse({
                'success': False,
                'message': f'Missing required OJT columns: {", ".join(missing_columns)}'
            }, status=400)
        # OJT_Company and OJT_Position are now optional
        
        # Create import record
        import_record = OJTImport.objects.create(
            coordinator=coordinator_username,
            batch_year=batch_year,
            course=course,
            file_name=file.name
        )
        
        created_count = 0
        skipped_count = 0
        errors = []
        
        for index, row in df.iterrows():
            print(f"--- Processing Row {index+2} ---")
            try:
                # --- Field Extraction and Cleaning ---
                ctu_id = str(row.get('CTU_ID', '')).strip()
                first_name = str(row.get('First_Name', '')).strip()
                middle_name = str(row.get('Middle_Name', '')).strip() if pd.notna(row.get('Middle_Name')) else ''
                last_name = str(row.get('Last_Name', '')).strip()
                gender = str(row.get('Gender', '')).strip().upper()
                
                # --- Birthdate Parsing ---
                birthdate = None
                birthdate_raw = row.get('Birthdate')
                print(f"Row {index+2} - Raw Birthdate: '{birthdate_raw}', Type: {type(birthdate_raw)}")
                if pd.notna(birthdate_raw):
                    try:
                        # This robustly handles Timestamps, datetime objects, and various string formats
                        dt_object = pd.to_datetime(birthdate_raw)
                        birthdate = dt_object.date()
                        print(f"Row {index+2} - Parsed birthdate successfully: {birthdate}")
                    except Exception as e:
                        print(f"Row {index+2} - FAILED to parse birthdate. Error: {e}")
                        birthdate = None
                
                # --- Validation Check ---
                required_data = {
                    "CTU_ID": ctu_id,
                    "First_Name": first_name,
                    "Last_Name": last_name,
                    "Gender": gender,
                    "Birthdate": birthdate
                }
                missing_fields = [key for key, value in required_data.items() if not value]

                if missing_fields:
                    error_msg = f"Row {index + 2}: Missing or invalid required fields - {', '.join(missing_fields)}"
                    print(f"SKIPPING: {error_msg}")
                    errors.append(error_msg)
                    skipped_count += 1
                    continue
                
                # --- Gender Validation ---
                if gender not in ['M', 'F']:
                    error_msg = f"Row {index + 2}: Gender must be 'M' or 'F', but was '{gender}'"
                    print(f"SKIPPING: {error_msg}")
                    errors.append(error_msg)
                    skipped_count += 1
                    continue
                
                # Check if OJT record already exists
                if User.objects.filter(acc_username=ctu_id).exists():
                    error_msg = f"Row {index + 2}: CTU ID {ctu_id} already exists in OJT data"
                    print(f"SKIPPING: {error_msg}")
                    errors.append(error_msg)
                    skipped_count += 1
                    continue
                
                # --- Create OJT record ---
                ojt_data = User.objects.create(
                    acc_username=ctu_id,
                    acc_password=birthdate,
                    birthdate=birthdate,
                    user_status='active',
                    f_name=first_name,
                    m_name=middle_name,
                    l_name=last_name,
                    gender=gender,
                    phone_num=str(row.get('Phone_Number', '')).strip() if pd.notna(row.get('Phone_Number')) else '',
                    address=str(row.get('Address', '')).strip() if pd.notna(row.get('Address')) else '',
                    civil_status=str(row.get('Civil_Status', '')).strip() if pd.notna(row.get('Civil_Status')) else '',
                    social_media=str(row.get('Social_Media', '')).strip() if pd.notna(row.get('Social_Media')) else '',
                    year_graduated=int(batch_year) if batch_year.isdigit() else None,
                    course=course,
                    account_type=AccountType.objects.get(ojt=True, admin=False, peso=False, user=False, coordinator=False),
                )
                
                print(f"SUCCESS: Created OJT record for CTU_ID {ctu_id}")
                created_count += 1
                
            except Exception as e:
                error_msg = f"Row {index + 2}: An unexpected error occurred - {str(e)}"
                print(f"ERROR: {error_msg}")
                errors.append(error_msg)
                skipped_count += 1
                continue
        
        # Update import record
        import_record.records_imported = created_count
        if errors:
            import_record.status = 'Partial' if created_count > 0 else 'Failed'
        import_record.save()
        
        return JsonResponse({
            'success': True,
            'message': f'OJT import completed. Created: {created_count}, Skipped: {skipped_count}',
            'created_count': created_count,
            'skipped_count': skipped_count,
            'errors': errors[:10]  # Limit errors to first 10
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Import failed: {str(e)}'}, status=500)

# OJT statistics for coordinators
@csrf_exempt
@require_http_methods(["GET"])
def ojt_statistics_view(request):
    try:
        coordinator_username = request.GET.get('coordinator', '')
        
        # Get OJT data for this coordinator only
        ojt_data = User.objects.filter(account_type__ojt=True) # Only OJT users, no coordinator filter
        
        # Group by batch year
        years_data = {}
        for ojt in ojt_data:
            year = ojt.year_graduated
            if year not in years_data:
                years_data[year] = 0
            years_data[year] += 1
        
        # Convert to list format
        years_list = [{'year': year, 'count': count} for year, count in years_data.items()]
        years_list.sort(key=lambda x: x['year'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'years': years_list,
            'total_records': ojt_data.count()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# OJT data by year for coordinators
@csrf_exempt
@require_http_methods(["GET"])
def ojt_by_year_view(request):
    try:
        year = request.GET.get('year', '')
        coordinator_username = request.GET.get('coordinator', '')
        
        if not year:
            return JsonResponse({'success': False, 'message': 'Year parameter is required'}, status=400)
        
        ojt_data = User.objects.filter(year_graduated=year, account_type__ojt=True) # Only OJT users, no coordinator filter
        
        ojt_list = []
        for ojt in ojt_data:
            ojt_list.append({
                'id': ojt.user_id,
                'ctu_id': ojt.acc_username,
                'first_name': ojt.f_name,
                'middle_name': ojt.m_name,
                'last_name': ojt.l_name,
                'gender': ojt.gender,
                'birthdate': ojt.birthdate,
                'age': ojt.age,  # Added age field
                'phone_number': ojt.phone_num,
                'address': ojt.address,
                'civil_status': ojt.civil_status,
                'social_media': ojt.social_media,
                'course': ojt.course,
                'ojt_company': None, # No longer stored in User model
                'ojt_position': None, # No longer stored in User model
                'ojt_start_date': None, # No longer stored in User model
                'ojt_end_date': None, # No longer stored in User model
                'ojt_supervisor': None, # No longer stored in User model
                'ojt_performance_rating': None, # No longer stored in User model
                'ojt_certificate': None, # No longer stored in User model
                'ojt_status': None, # No longer stored in User model
                'ojt_remarks': None, # No longer stored in User model
                'imported_by': ojt.acc_username,
                'import_date': None, # No longer stored in User model
                'batch_year': ojt.year_graduated,
            })
        
        return JsonResponse({
            'success': True,
            'ojt_data': ojt_list
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
