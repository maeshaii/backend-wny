from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.core.files.storage import default_storage
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date
from apps.shared.models import User, AccountType, User, OJTImport, Notification, Post, PostCategory, Like, Comment, Repost
import json
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken
import pandas as pd
import io
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from collections import Counter
from apps.shared.models import Question
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Value, CharField
from django.db.models.functions import Concat, Coalesce
from rest_framework.decorators import api_view

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'success': True, 'message': 'CSRF cookie set'})

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Utility: build profile_pic URL with cache-busting when possible
def build_profile_pic_url(user):
    try:
        pic = getattr(user, 'profile_pic', None)
        if pic:
            url = pic.url
            try:
                modified = default_storage.get_modified_time(pic.name)
                if modified:
                    return f"{url}?t={int(modified.timestamp())}"
            except Exception:
                pass
            return url
    except Exception:
        pass
    return None

# Utility: extract current user from Authorization header (Bearer/JWT) robustly
def get_current_user_from_request(request):
    auth_header = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return None
    try:
        parts = auth_header.strip().split()
        token = None
        if len(parts) == 2:
            # Format: "Bearer <token>" or "JWT <token>"
            token = parts[1].strip('"')
        else:
            # Sometimes the raw token may be provided
            token = parts[0].strip('"')
        if not token:
            return None
        from rest_framework_simplejwt.tokens import AccessToken
        access_token = AccessToken(token)
        current_user_id = access_token.get('user_id') or access_token.get('id')
        if not current_user_id:
            return None
        return User.objects.get(user_id=int(current_user_id))
    except Exception:
        return None

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
                    'profile_bio': user.profile_bio,
                    'profile_pic': build_profile_pic_url(user),
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
            'profile_bio': user.profile_bio,
            'profile_pic': build_profile_pic_url(user),
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
    notif_list = []
    import re
    for n in notifications:
        entry = {
            'id': n.notification_id,
            'type': n.notif_type,
            'subject': getattr(n, 'subject', None) or 'Tracker Form Reminder',
            'content': n.notifi_content,
            'date': n.notif_date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        # Extract follower profile link if present (e.g., /alumni/profile/<id>)
        try:
            match = re.search(r"/alumni/profile/(\d+)", n.notifi_content or '')
            if match:
                follower_id = int(match.group(1))
                entry['link'] = f"/alumni/profile/{follower_id}"
                entry['link_user_id'] = follower_id
        except Exception:
            pass
        notif_list.append(entry)
    return JsonResponse({'success': True, 'notifications': notif_list})

@csrf_exempt
@require_http_methods(["GET"])
def users_list_view(request):
    current_user_id = request.GET.get('current_user_id')
    try:
        # Parse current_user_id to int if possible for safety
        try:
            current_user_id_int = int(current_user_id) if current_user_id is not None else None
        except (TypeError, ValueError):
            current_user_id_int = None
        
        # Exclude admin users and the current logged-in user, pick 10 at random
        users_qs = User.objects.filter(account_type__admin=False)
        if current_user_id_int is not None:
            users_qs = users_qs.exclude(user_id=current_user_id_int)
        users = users_qs.order_by('?')[:10]
        
        users_data = [
            {
                'id': u.user_id,
                'name': f"{u.f_name} {u.l_name}",
                'profile_pic': build_profile_pic_url(u),
                'batch': u.year_graduated,
            }
            for u in users
        ]
        return JsonResponse({'success': True, 'users': users_data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

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
                
                # --- Calculate Age ---
                age = None
                if birthdate:
                    from datetime import date
                    today = date.today()
                    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
                    print(f"Row {index+2} - Calculated age: {age}")
                
                # --- Parse OJT Start/End Dates ---
                ojt_start_date = None
                ojt_end_date = None
                
                # Try different possible column names for start date
                start_date_raw = row.get('Ojt_Start_Date') or row.get('Start_Date')
                print(f"Row {index+2} - Raw Start Date: '{start_date_raw}', Type: {type(start_date_raw)}")
                if pd.notna(start_date_raw):
                    try:
                        ojt_start_date = pd.to_datetime(start_date_raw, dayfirst=True).date()
                        print(f"Row {index+2} - Parsed start date successfully: {ojt_start_date}")
                    except Exception as e:
                        print(f"Row {index+2} - FAILED to parse start date. Error: {e}")
                        ojt_start_date = None
                
                # Try different possible column names for end date
                end_date_raw = row.get('Ojt_End_Date') or row.get('End_Date')
                print(f"Row {index+2} - Raw End Date: '{end_date_raw}', Type: {type(end_date_raw)}")
                if pd.notna(end_date_raw):
                    try:
                        ojt_end_date = pd.to_datetime(end_date_raw, dayfirst=True).date()
                        print(f"Row {index+2} - Parsed end date successfully: {ojt_end_date}")
                    except Exception as e:
                        print(f"Row {index+2} - FAILED to parse end date. Error: {e}")
                        ojt_end_date = None

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
                    age=age,
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
                    date_started=ojt_start_date,
                    ojt_end_date=ojt_end_date,
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
                'age': ojt.calculated_age,  # Use calculated age property
                'phone_number': ojt.phone_num,
                'address': ojt.address,
                'civil_status': ojt.civil_status,
                'social_media': ojt.social_media,
                'course': ojt.course,
                'ojt_start_date': ojt.date_started,  # Map to date_started field
                'ojt_end_date': ojt.ojt_end_date,    # Map to ojt_end_date field
                'batch_year': ojt.year_graduated,
            })
        
        return JsonResponse({
            'success': True,
            'ojt_data': ojt_list
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "PUT"])
def profile_bio_view(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        if request.method == "GET":
            return JsonResponse({'profile_bio': user.profile_bio or ''})
        elif request.method == "PUT":
            data = json.loads(request.body)
            user.profile_bio = data.get('profile_bio', '')
            user.save()
            return JsonResponse({'profile_bio': user.profile_bio})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)



@csrf_exempt
def update_resume(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return JsonResponse({"error": "Missing user_id"}, status=400)

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if request.method in ['POST', 'PUT']:
        resume_file = request.FILES.get('resume')
        if not resume_file:
            return JsonResponse({"error": "No resume file uploaded"}, status=400)

        # Optional: File size limit check
        if resume_file.size > 10 * 1024 * 1024:
            return JsonResponse({"error": "Resume file exceeds 10MB limit"}, status=400)

        filename = default_storage.save(f"resumes/{user_id}_{resume_file.name}", resume_file)
        user.profile_resume = filename
        user.save()
        return JsonResponse({
            "message": "Resume uploaded",
            "resume": user.profile_resume.url if user.profile_resume else ""
        })


    elif request.method == 'DELETE':
        if user.profile_resume:
            file_path = os.path.join(settings.MEDIA_ROOT, user.profile_resume.name)
            if os.path.exists(file_path):
                os.remove(file_path)
            user.profile_resume = None
            user.save()
            return JsonResponse({"message": "Resume deleted"})
        return JsonResponse({"error": "No resume found"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@api_view(['PUT'])
@parser_classes([MultiPartParser])
def update_alumni_profile(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return Response({'message': 'Missing user_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(user_id=user_id)

        bio = request.data.get('bio')
        if bio is not None:
            user.profile_bio = bio

        if 'profile_pic' in request.FILES:
            user.profile_pic = request.FILES['profile_pic']

        user.save()

        return Response({
            'user': {
                'id': user.user_id,
                'name': f"{user.f_name} {user.l_name}",
                'profile_pic': user.profile_pic.url if user.profile_pic else None,
                'bio': user.profile_bio,
            }
        })

    except User.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
def search_alumni(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return Response([])

    # Combine first, middle (nullable), and last names
    results = User.objects.annotate(
        full_name=Concat(
            'f_name',
            Value(' '),
            Coalesce('m_name', Value('')),
            Value(' '),
            'l_name',
            output_field=CharField()
        )
    ).filter(full_name__icontains=query)[:10]

    data = [{
        'user_id': a.user_id,
        'name': f"{a.f_name} {a.m_name or ''} {a.l_name}".strip(),
        'course': a.course,
        'year_graduated': a.year_graduated,
        'profile_pic': build_profile_pic_url(a)
    } for a in results]

    return Response(data)


@api_view(['DELETE'])
def delete_alumni_profile_pic(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return Response({'message': 'Missing user_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(user_id=user_id)
        if user.profile_pic:
            # Delete the file from storage
            try:
                file_path = user.profile_pic.path
            except Exception:
                file_path = None
            user.profile_pic.delete(save=False)
            user.profile_pic = None
            user.save()
            # Also remove local file if path is available
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
        return Response({'success': True})
    except User.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



# mobile side

@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def posts_view(request):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
        return response

    if request.method == "GET":
        try:
            # Get all posts with user and category information
            posts = Post.objects.select_related('user', 'post_cat').order_by('-post_id')
            posts_data = []
            
            for post in posts:
                # Get repost information for THIS specific post
                reposts = Repost.objects.filter(post=post).select_related('user')
                repost_data = []
                
                for repost in reposts:
                    repost_data.append({
                        'repost_id': repost.repost_id,
                        'repost_date': repost.repost_date.isoformat(),
                        'user': {
                            'user_id': repost.user.user_id,
                            'f_name': repost.user.f_name,
                            'l_name': repost.user.l_name,
                            'profile_pic': build_profile_pic_url(repost.user),
                        }
                    })
                
                # Get comments for THIS specific post
                comments = Comment.objects.filter(post=post).select_related('user').order_by('-date_created')
                comments_data = []
                
                for comment in comments:
                    comments_data.append({
                        'comment_id': comment.comment_id,
                        'comment_content': comment.comment_content,
                        'date_created': comment.date_created.isoformat() if comment.date_created else None,
                        'user': {
                            'user_id': comment.user.user_id,
                            'f_name': comment.user.f_name,
                            'l_name': comment.user.l_name,
                            'profile_pic': build_profile_pic_url(comment.user),
                        }
                    })
                
                # Get likes for THIS specific post with user information
                likes = Like.objects.filter(post=post).select_related('user')
                likes_data = []
                
                for like in likes:
                    likes_data.append({
                        'like_id': like.like_id,
                        'user_id': like.user.user_id,
                        'f_name': like.user.f_name,
                        'l_name': like.user.l_name,
                        'profile_pic': build_profile_pic_url(like.user),
                    })

                posts_data.append({
                    'post_id': post.post_id,
                    'post_title': post.post_title,
                    'post_content': post.post_content,
                    'post_image': post.post_image.url if post.post_image else None,
                    'type': post.type,
                    'created_at': post.created_at.isoformat() if hasattr(post, 'created_at') else None,
                    'likes_count': len(likes_data),
                    'comments_count': post.comments.count(),
                    'reposts_count': post.reposts.count(),
                    'likes': likes_data,
                    'reposts': repost_data,
                    'comments': comments_data,
                    'user': {
                        'user_id': post.user.user_id,
                        'f_name': post.user.f_name,
                        'l_name': post.user.l_name,
                        'profile_pic': build_profile_pic_url(post.user),
                    },
                    'category': {
                        'post_cat_id': post.post_cat.post_cat_id if post.post_cat else None,
                        'events': post.post_cat.events if post.post_cat else False,
                        'announcements': post.post_cat.announcements if post.post_cat else False,
                        'donation': post.post_cat.donation if post.post_cat else False,
                        'personal': post.post_cat.personal if post.post_cat else False,
                    }
                })
            
            return JsonResponse({'posts': posts_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            print(f"DEBUG: Received post data: {data}")
            
            # Get user from token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            token = auth_header.split(' ')[1]
            # Validate JWT token and get user
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                from django.contrib.auth import get_user_model
                
                # Decode the token
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = User.objects.get(user_id=user_id)
                print(f"DEBUG: Found user: {user.user_id}")
            except Exception as e:
                print(f"DEBUG: Token error: {e}")
                return JsonResponse({'error': 'Invalid token'}, status=401)
            
            # Validate post category exists
            post_cat_id = data.get('post_cat_id')
            try:
                post_category = PostCategory.objects.get(post_cat_id=post_cat_id)
                print(f"DEBUG: Found category: {post_category.post_cat_id}")
            except PostCategory.DoesNotExist:
                print(f"DEBUG: Category {post_cat_id} not found")
                return JsonResponse({'error': 'Invalid post category'}, status=400)
            
            # Create the post
            post_image = data.get('post_image', '')
            post = None  # Initialize post variable
            
            if post_image == '' or post_image.startswith('file://'):
                post_image = None  # Convert empty string or local file path to None for ImageField
                post = Post.objects.create(
                    user=user,
                    post_cat=post_category,
                    post_title=data.get('post_title', ''),
                    post_content=data.get('post_content', ''),
                    post_image=post_image,
                    type=data.get('type', 'personal')
                )
            elif post_image.startswith('data:image/'):
                # Handle base64 image data
                import base64
                from django.core.files.base import ContentFile
                import uuid
                
                try:
                    # Extract base64 data
                    format, imgstr = post_image.split(';base64,')
                    ext = format.split('/')[-1]
                    
                    # Create file name
                    filename = f"post_image_{uuid.uuid4()}.{ext}"
                    
                    # Convert base64 to file
                    image_data = base64.b64decode(imgstr)
                    image_file = ContentFile(image_data, name=filename)
                    
                    post = Post.objects.create(
                        user=user,
                        post_cat=post_category,
                        post_title=data.get('post_title', ''),
                        post_content=data.get('post_content', ''),
                        post_image=image_file,
                        type=data.get('type', 'personal')
                    )
                except Exception as e:
                    print(f"DEBUG: Error handling base64 image: {e}")
                    post = Post.objects.create(
                        user=user,
                        post_cat=post_category,
                        post_title=data.get('post_title', ''),
                        post_content=data.get('post_content', ''),
                        post_image=None,
                        type=data.get('type', 'personal')
                    )
            else:
                # If it's a URL or path, try to use it directly (rare)
                post = Post.objects.create(
                    user=user,
                    post_cat=post_category,
                    post_title=data.get('post_title', ''),
                    post_content=data.get('post_content', ''),
                    post_image=None,
                    type=data.get('type', 'personal')
                )
            print(f"DEBUG: Created post: {post.post_id}")
            
            return JsonResponse({
                'success': True,
                'post_id': post.post_id,
                'post_image': post.post_image.url if post.post_image else None,
                'message': 'Post created successfully'
            })
        except Exception as e:
            import traceback
            print(f"DEBUG: Error creating post: {str(e)}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST", "DELETE", "OPTIONS"])
def post_like_view(request, post_id):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
        return response

    try:
        post = Post.objects.get(post_id=post_id)
        
        # Get user from token
        auth_header = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(user_id=user_id)
        except Exception as e:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        if request.method == "POST":
            # Like the post
            like, created = Like.objects.get_or_create(user=user, post=post)
            if created:
                # Create notification for post owner (only if the liker is not the post owner)
                if user.user_id != post.user.user_id:
                    Notification.objects.create(
                        user=post.user,
                        notif_type='like',
                        subject='Post Liked',
                        notifi_content=f"{user.f_name} {user.l_name} liked your post",
                        notif_date=timezone.now()
                    )
                return JsonResponse({'success': True, 'message': 'Post liked'})
            else:
                return JsonResponse({'success': False, 'message': 'Post already liked'})
        elif request.method == "DELETE":
            # Unlike the post
            try:
                like = Like.objects.get(user=user, post=post)
                like.delete()
                return JsonResponse({'success': True, 'message': 'Post unliked'})
            except Like.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Post not liked'})
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def post_comments_view(request, post_id):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
        return response

    try:
        post = Post.objects.get(post_id=post_id)
        
        if request.method == "GET":
            # Get comments for the post
            comments = Comment.objects.filter(post=post).select_related('user').order_by('-date_created')
            comments_data = []
            
            for comment in comments:
                comments_data.append({
                    'comment_id': comment.comment_id,
                    'comment_content': comment.comment_content,
                    'date_created': comment.date_created.isoformat(),
                    'user': {
                        'user_id': comment.user.user_id,
                        'f_name': comment.user.f_name,
                        'l_name': comment.user.l_name,
                        'profile_pic': build_profile_pic_url(comment.user),
                    }
                })
            
            return JsonResponse({'comments': comments_data})
        elif request.method == "POST":
            data = json.loads(request.body)
            
            # Get user from token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            token = auth_header.split(' ')[1]
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = User.objects.get(user_id=user_id)
            except Exception as e:
                return JsonResponse({'error': 'Invalid token'}, status=401)
            
            # Create comment
            comment = Comment.objects.create(
                user=user,
                post=post,
                comment_content=data.get('comment_content', ''),
                date_created=timezone.now()
            )
            
            # Create notification for post owner 
            if user.user_id != post.user.user_id:
                Notification.objects.create(
                    user=post.user,
                    notif_type='comment',
                    subject='Post Commented',
                    notifi_content=f"{user.f_name} {user.l_name} commented on your post",
                    notif_date=timezone.now()
                )
            
            return JsonResponse({
                'success': True, 
                'message': 'Comment added',
                'comment_id': comment.comment_id
            })
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE", "OPTIONS"])
def post_delete_view(request, post_id):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
        return response

    try:
        post = Post.objects.get(post_id=post_id)
        
        # Get user from token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(user_id=user_id)
        except Exception as e:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        # Check if user owns the post
        if post.user.user_id != user.user_id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        post.delete()
        return JsonResponse({'success': True, 'message': 'Post deleted'})
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def post_categories_view(request):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        return response

    try:
        categories = PostCategory.objects.all()
        categories_data = []
        
        for category in categories:
            categories_data.append({
                'post_cat_id': category.post_cat_id,
                'events': category.events,
                'announcements': category.announcements,
                'donation': category.donation,
                'personal': category.personal,
            })
        
        return JsonResponse({'categories': categories_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def post_repost_view(request, post_id):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
        return response

    try:
        post = Post.objects.get(post_id=post_id)
        
        # Get user from token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(user_id=user_id)
        except Exception as e:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        # Check if user already reposted this post
        existing_repost = Repost.objects.filter(user=user, post=post).first()
        if existing_repost:
            return JsonResponse({'error': 'You have already reposted this'}, status=400)
        
        # Create repost
        repost = Repost.objects.create(
            user=user,
            post=post,
            repost_date=timezone.now()
        )
        
        # Create notification for post owner (only if the reposter is not the post owner)
        if user.user_id != post.user.user_id:
            Notification.objects.create(
                user=post.user,
                notif_type='repost',
                subject='Post Reposted',
                notifi_content=f"{user.f_name} {user.l_name} reposted your post",
                notif_date=timezone.now()
            )
        
        return JsonResponse({
            'success': True,
            'repost_id': repost.repost_id,
            'message': 'Post reposted successfully'
        })
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE", "OPTIONS"])
def repost_delete_view(request, repost_id):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
        return response

    try:
        repost = Repost.objects.get(repost_id=repost_id)
        
        # Get user from token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(user_id=user_id)
        except Exception as e:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        # Check if user owns the repost
        if repost.user.user_id != user.user_id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        repost.delete()
        return JsonResponse({'success': True, 'message': 'Repost deleted'})
    except Repost.DoesNotExist:
        return JsonResponse({'error': 'Repost not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def alumni_followers_view(request, user_id):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
        return response

    try:
        user = User.objects.get(user_id=user_id)
        from apps.shared.models import Follow
        followers = Follow.objects.filter(following=user).select_related('follower')
        if not followers.exists():
            return JsonResponse({
                'success': True,
                'followers': [],
                'message': 'no followers',
                'count': 0
            })
        followers_data = []
        for follow_obj in followers:
            follower = follow_obj.follower
            followers_data.append({
                'user_id': follower.user_id,
                'ctu_id': follower.acc_username,
                'name': f"{follower.f_name} {follower.l_name}",
                'profile_pic': build_profile_pic_url(follower),
                'followed_at': follow_obj.followed_at.isoformat()
            })
        return JsonResponse({
            'success': True,
            'followers': followers_data,
            'count': len(followers_data)
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def alumni_following_view(request, user_id):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
        return response

    try:
        user = User.objects.get(user_id=user_id)
        from apps.shared.models import Follow
        following = Follow.objects.filter(follower=user).select_related('following')
        if not following.exists():
            return JsonResponse({
                'success': True,
                'following': [],
                'message': 'no following',
                'count': 0
            })
        following_data = []
        for follow_obj in following:
            followed_user = follow_obj.following
            following_data.append({
                'user_id': followed_user.user_id,
                'ctu_id': followed_user.acc_username,
                'name': f"{followed_user.f_name} {followed_user.l_name}",
                'profile_pic': build_profile_pic_url(followed_user),
                'followed_at': follow_obj.followed_at.isoformat()
            })
        return JsonResponse({
            'success': True,
            'following': following_data,
            'count': len(following_data)
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.shared.models import Follow

@csrf_exempt
@require_http_methods(["POST", "DELETE", "OPTIONS"])
def follow_user_view(request, user_id):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
        return response

    try:
        # Authenticate via JWT manually to avoid issues with custom user
        current_user = get_current_user_from_request(request)
        if not current_user:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        user_to_follow = User.objects.get(user_id=user_id)

        if current_user.user_id == user_to_follow.user_id:
            return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

        if request.method == 'POST':
            follow_obj, created = Follow.objects.get_or_create(
                follower=current_user,
                following=user_to_follow
            )
            if created:
                # Notify the followed user
                try:
                    Notification.objects.create(
                        user=user_to_follow,
                        notif_type='follow',
                        subject='New Follower',
                        notifi_content=f"{current_user.f_name} {current_user.l_name} started following you. View profile: /alumni/profile/{current_user.user_id}",
                        notif_date=timezone.now()
                    )
                except Exception:
                    pass
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully followed {user_to_follow.f_name} {user_to_follow.l_name}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Already following this user'
                }, status=400)

        elif request.method == 'DELETE':
            try:
                follow_obj = Follow.objects.get(
                    follower=current_user,
                    following=user_to_follow
                )
                follow_obj.delete()
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully unfollowed {user_to_follow.f_name} {user_to_follow.l_name}'
                })
            except Follow.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Not following this user'
                }, status=400)

    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def check_follow_status_view(request, user_id):
    if request.method == "OPTIONS":
        response = JsonResponse({'detail': 'OK'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
        return response

    try:
        # Get the user to check
        user_to_check = User.objects.get(user_id=user_id)
        
        # Get the current user from token
        auth_header = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            # If no authentication, return not following
            return JsonResponse({
                'success': True,
                'is_following': False
            })
        
        token = auth_header.split(' ')[1]
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            current_user_id = access_token.get('user_id') or access_token.get('id')
            current_user = User.objects.get(user_id=int(current_user_id))
        except Exception as e:
            # If token is invalid, return not following
            return JsonResponse({
                'success': True,
                'is_following': False
            })
        
        # Check if current user is following the target user
        from apps.shared.models import Follow
        is_following = Follow.objects.filter(
            follower=current_user,
            following=user_to_check
        ).exists()
        
        return JsonResponse({
            'success': True,
            'is_following': is_following
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
