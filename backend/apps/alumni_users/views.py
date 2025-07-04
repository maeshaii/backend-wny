from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.shared.models import User

# Create your views here.

@csrf_exempt
@require_http_methods(["GET"])
def alumni_list_view(request):
    year = request.GET.get('year')
    alumni_qs = User.objects.filter(account_type__user=True)
    if year:
        alumni_qs = alumni_qs.filter(year_graduated=year)
    alumni_data = [
        {
            'id': a.user_id,
            'ctu_id': a.acc_username,
            'name': f"{a.f_name} {a.m_name or ''} {a.l_name}",
            'course': a.course,
            'batch': a.year_graduated,
            'status': a.user_status,
            'gender': a.gender,
            'birthdate': str(a.acc_password),
            'phone': a.phone_num,
            'address': a.address,
        }
        for a in alumni_qs
    ]
    return JsonResponse({'success': True, 'alumni': alumni_data})
