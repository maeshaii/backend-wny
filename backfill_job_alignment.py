import os
import django

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    from apps.shared.models import User, TrackerResponse, Suc, Ched, Standard
    from job_alignment import is_job_aligned_excel

    updated = 0
    for user in User.objects.filter(account_type__user=True):
        latest_response = TrackerResponse.objects.filter(user=user).order_by('-submitted_at').first()
        if not latest_response:
            continue
        answers = latest_response.answers or {}
        job_code = answers.get('Job Code') or answers.get('job_code')
        course = getattr(user, 'course', None)
        if not job_code or not course:
            continue
        # Find the latest Standard record for this user
        std = Standard.objects.filter(tracker_form__user=user).order_by('-standard_id').first()
        if not std:
            continue
        suc = std.suc if std and std.suc else None
        ched = std.ched if std and std.ched else None
        if is_job_aligned_excel(course, job_code):
            if suc:
                suc.job_alignment_count += 1
                suc.save()
            if ched:
                ched.job_alignment_count += 1
                ched.save()
            updated += 1
    print(f'Updated job alignment for {updated} alumni.')

if __name__ == '__main__':
    main() 