import os
import django

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    from apps.shared.models import User, TrackerResponse

    updated = 0
    for user in User.objects.filter(account_type__user=True):
        latest_response = TrackerResponse.objects.filter(user=user).order_by('-submitted_at').first()
        if not latest_response:
            continue
        answers = latest_response.answers or {}
        q21 = answers.get('21') or answers.get(21)
        if not q21:
            continue
        status = str(q21).strip().lower()
        if status in ['yes', 'employed', 'presently employed', 'currently employed']:
            user.user_status = 'employed'
        elif status in ['no', 'unemployed', 'not employed']:
            user.user_status = 'unemployed'
        else:
            continue
        user.save()
        updated += 1
    print(f'Updated {updated} alumni user_status fields.')

if __name__ == '__main__':
    main() 