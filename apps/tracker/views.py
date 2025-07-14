from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from apps.shared.models import QuestionCategory, TrackerResponse, Question, TrackerForm

# Create your views here.

@csrf_exempt
@require_http_methods(["GET"])
def tracker_questions_view(request):
    categories = []
    for cat in QuestionCategory.objects.prefetch_related('questions').all():
        categories.append({
            "id": cat.id,
            "title": cat.title,
            "description": cat.description,
            "questions": [
                {
                    "id": q.id,
                    "text": q.text,
                    "type": q.type,
                    "options": q.options or []
                }
                for q in cat.questions.all()
            ]
        })
    return JsonResponse({"success": True, "categories": categories})

@csrf_exempt
@require_http_methods(["GET"])
def tracker_responses_view(request):
    from apps.shared.models import User
    responses = []
    # Define the basic user fields to merge
    basic_fields = {
        'First Name': 'f_name',
        'Middle Name': 'm_name',
        'Last Name': 'l_name',
        'Gender': 'gender',
        'Birthdate': 'birthdate',
        'Phone Number': 'phone_num',
        'Address': 'address',
        'Social Media': 'social_media',
        'Civil Status': 'civil_status',
        'Age': 'age',
        'Email': 'email',
        'Program Name': 'program',
        'Status': 'user_status',
    }
    for resp in TrackerResponse.objects.select_related('user').all():
        user = resp.user
        merged_answers = resp.answers.copy() if resp.answers else {}
        # Fill in missing basic fields from User model
        for label, field in basic_fields.items():
            if label not in merged_answers or merged_answers[label] in [None, '', 'No answer']:
                value = getattr(user, field, None)
                if value is not None and value != '':
                    merged_answers[label] = str(value)
        responses.append({
            'user_id': user.user_id,
            'name': f'{user.f_name} {user.l_name}',
            'answers': merged_answers
        })
    return JsonResponse({'success': True, 'responses': responses})

@csrf_exempt
@require_http_methods(["GET"])
def tracker_responses_by_user_view(request, user_id):
    try:
        # Ensure user_id is an integer
        user_id = int(user_id)
        from apps.shared.models import User
        user = User.objects.get(user_id=user_id)
        responses = []
        for resp in TrackerResponse.objects.select_related('user').filter(user__user_id=user_id):
            responses.append({
                'name': f'{resp.user.f_name} {resp.user.l_name}',
                'answers': resp.answers,
                'submitted_at': resp.submitted_at
            })
        return JsonResponse({'success': True, 'responses': responses})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_category_view(request):
    data = json.loads(request.body)
    title = data.get('title')
    description = data.get('description', '')
    if not title:
        return JsonResponse({'success': False, 'message': 'Title is required'}, status=400)
    cat = QuestionCategory.objects.create(title=title, description=description)
    return JsonResponse({'success': True, 'category': {'id': cat.id, 'title': cat.title, 'description': cat.description, 'questions': []}})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_category_view(request, category_id):
    try:
        cat = QuestionCategory.objects.get(id=category_id)
        cat.delete()
        return JsonResponse({'success': True})
    except QuestionCategory.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Category not found'}, status=404)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_question_view(request, question_id):
    try:
        q = Question.objects.get(id=question_id)
        q.delete()
        return JsonResponse({'success': True})
    except Question.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Question not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def add_question_view(request):
    data = json.loads(request.body)
    category_id = data.get('category_id')
    text = data.get('text')
    qtype = data.get('type')
    options = data.get('options', [])
    if not (category_id and text and qtype):
        return JsonResponse({'success': False, 'message': 'Missing required fields'}, status=400)
    try:
        category = QuestionCategory.objects.get(id=category_id)
    except QuestionCategory.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Category not found'}, status=404)
    q = Question.objects.create(category=category, text=text, type=qtype, options=options)
    return JsonResponse({'success': True, 'question': {
        'id': q.id, 'text': q.text, 'type': q.type, 'options': q.options or []
    }})

@csrf_exempt
@require_http_methods(["PUT"])
def update_category_view(request, category_id):
    data = json.loads(request.body)
    title = data.get('title')
    description = data.get('description', '')
    try:
        cat = QuestionCategory.objects.get(id=category_id)
        if title:
            cat.title = title
        cat.description = description
        cat.save()
        return JsonResponse({'success': True, 'category': {'id': cat.id, 'title': cat.title, 'description': cat.description}})
    except QuestionCategory.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Category not found'}, status=404)

@csrf_exempt
@require_http_methods(["PUT"])
def update_question_view(request, question_id):
    data = json.loads(request.body)
    text = data.get('text')
    qtype = data.get('type')
    options = data.get('options', [])
    try:
        q = Question.objects.get(id=question_id)
        if text:
            q.text = text
        if qtype:
            q.type = qtype
        q.options = options
        q.save()
        return JsonResponse({'success': True, 'question': {'id': q.id, 'text': q.text, 'type': q.type, 'options': q.options or []}})
    except Question.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Question not found'}, status=404)

@csrf_exempt
@require_http_methods(["PUT"])
def update_tracker_form_title_view(request, tracker_form_id):
    import json
    try:
        data = json.loads(request.body)
        title = data.get('title')
        if title is None:
            return JsonResponse({'success': False, 'message': 'Title is required'}, status=400)
        form = TrackerForm.objects.get(pk=tracker_form_id)
        form.title = title
        form.save()
        return JsonResponse({'success': True, 'title': form.title})
    except TrackerForm.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'TrackerForm not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def tracker_form_view(request, tracker_form_id):
    try:
        form = TrackerForm.objects.get(pk=tracker_form_id)
        return JsonResponse({'success': True, 'title': form.title or 'Alumni Tracker Form'})
    except TrackerForm.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'TrackerForm not found'}, status=404)

@csrf_exempt
@require_http_methods(["GET"])
def check_user_tracker_status_view(request):
    from apps.shared.models import User, TrackerResponse
    
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'user_id is required'}, status=400)
    
    try:
        user = User.objects.get(user_id=user_id)
        existing_response = TrackerResponse.objects.filter(user=user).first()
        
        return JsonResponse({
            'success': True, 
            'has_submitted': existing_response is not None,
            'submitted_at': existing_response.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if existing_response else None
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def submit_tracker_response_view(request):
    import json
    from django.utils import timezone
    from apps.shared.models import TrackerResponse, User, Notification

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        answers = data.get('answers')
        if not user_id or not answers:
            return JsonResponse({'success': False, 'message': 'Missing user_id or answers'}, status=400)
        user = User.objects.get(pk=user_id)
        
        # Check if user has already submitted a response
        existing_response = TrackerResponse.objects.filter(user=user).first()
        if existing_response:
            return JsonResponse({'success': False, 'message': 'You have already submitted the tracker form'}, status=400)
        
        tr = TrackerResponse.objects.create(user=user, answers=answers, submitted_at=timezone.now())
        
        # Create a thank you notification
        Notification.objects.create(
            user=user,
            notif_type='CCICT',
            subject='Thank You for Completing the Tracker Form',
            notifi_content=f'Thank you {user.f_name} {user.l_name} for completing the alumni tracker form. Your response has been recorded successfully.',
            notif_date=timezone.now()
        )
        
        return JsonResponse({'success': True, 'message': 'Response recorded', 'user_id': user.user_id})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
