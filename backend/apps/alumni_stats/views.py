from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.shared.models import User
from collections import Counter

# Create your views here.

@csrf_exempt
@require_http_methods(["GET"])
def alumni_statistics_view(request):
    year = request.GET.get('year')
    course = request.GET.get('course')
    alumni_qs = User.objects.filter(account_type__user=True)
    if year and year != 'ALL':
        alumni_qs = alumni_qs.filter(year_graduated=year)
    if course and course != 'ALL':
        alumni_qs = alumni_qs.filter(course=course)
    # Count by employment status
    status_counts = Counter(alumni_qs.values_list('user_status', flat=True))
    # Count by year for year options
    year_counts = Counter(User.objects.filter(account_type__user=True).values_list('year_graduated', flat=True))
    filtered_year_counts = {y: c for y, c in year_counts.items() if y is not None}
    return JsonResponse({
        'success': True,
        'status_counts': dict(status_counts),
        'years': [
            {'year': year, 'count': count}
            for year, count in sorted(filtered_year_counts.items(), reverse=True)
        ]
    })
