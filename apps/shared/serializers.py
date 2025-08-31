"""
Serializers for shared app models: user, profile, academic info, employment, tracker, OJT, and related entities.
Consider splitting into multiple files if the number of serializers grows.
"""
from rest_framework import serializers
from .models import (
    User, UserProfile, AcademicInfo, EmploymentHistory, 
    TrackerData, OJTInfo, AccountType
)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model, including calculated age."""
    calculated_age = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = [
            'phone_num', 'email', 'address', 'home_address',
            'birthdate', 'age', 'calculated_age', 'civil_status',
            'social_media', 'profile_pic', 'profile_bio', 'profile_resume'
        ]


class AcademicInfoSerializer(serializers.ModelSerializer):
    """Serializer for AcademicInfo model."""
    class Meta:
        model = AcademicInfo
        fields = [
            'year_graduated', 'course', 'program', 'section', 'school_name',
            'pursue_further_study', 'q_pursue_study', 'q_study_start_date', 
            'q_post_graduate_degree', 'q_institution_name', 'q_units_obtained'
        ]


class EmploymentHistorySerializer(serializers.ModelSerializer):
    """Serializer for EmploymentHistory model."""
    class Meta:
        model = EmploymentHistory
        fields = [
            'company_name_current', 'position_current', 'sector_current',
            'employment_duration_current', 'salary_current', 'date_started',
            'company_address', 'job_alignment_status', 'job_alignment_category',
            'job_alignment_title', 'self_employed', 'high_position', 'absorbed',
            'awards_recognition_current', 'supporting_document_current',
            'supporting_document_awards_recognition', 'unemployment_reason'
        ]


class TrackerDataSerializer(serializers.ModelSerializer):
    """Serializer for TrackerData model."""
    class Meta:
        model = TrackerData
        fields = [
            'q_employment_status', 'q_employment_type', 'q_employment_permanent',
            'q_company_name', 'q_current_position', 'q_job_sector',
            'q_employment_duration', 'q_salary_range', 'q_awards_received',
            'q_awards_document', 'q_employment_document', 'q_unemployment_reason',
            'tracker_submitted_at', 'tracker_last_updated'
        ]


class OJTInfoSerializer(serializers.ModelSerializer):
    """Serializer for OJTInfo model."""
    class Meta:
        model = OJTInfo
        fields = [
            'ojt_end_date', 'job_code', 'ojtstatus'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Full serializer for User model, including related models."""
    profile = UserProfileSerializer(read_only=True)
    academic_info = AcademicInfoSerializer(read_only=True)
    employment = EmploymentHistorySerializer(read_only=True)
    tracker_data = TrackerDataSerializer(read_only=True)
    ojt_info = OJTInfoSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'user_id', 'acc_username', 'user_status', 'f_name', 'm_name', 'l_name',
            'gender', 'full_name', 'profile', 'academic_info', 'employment',
            'tracker_data', 'ojt_info', 'created_at', 'updated_at'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a User with nested related data."""
    profile_data = UserProfileSerializer(required=False)
    academic_data = AcademicInfoSerializer(required=False)
    employment_data = EmploymentHistorySerializer(required=False)
    tracker_data = TrackerDataSerializer(required=False)
    ojt_data = OJTInfoSerializer(required=False)
    
    class Meta:
        model = User
        fields = [
            'acc_username', 'acc_password', 'user_status', 'f_name', 'm_name', 'l_name',
            'gender', 'account_type', 'profile_data', 'academic_data', 
            'employment_data', 'tracker_data', 'ojt_data'
        ]
    
    def create(self, validated_data):
        from .services import UserService
        
        # Extract nested data
        profile_data = validated_data.pop('profile_data', {})
        academic_data = validated_data.pop('academic_data', {})
        employment_data = validated_data.pop('employment_data', None)
        tracker_data = validated_data.pop('tracker_data', {})
        ojt_data = validated_data.pop('ojt_data', None)
        
        # Create user with all related models
        user = UserService.create_complete_user(
            user_data=validated_data,
            profile_data=profile_data,
            academic_data=academic_data,
            employment_data=employment_data,
            tracker_data=tracker_data,
            ojt_data=ojt_data
        )
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a User and related models."""
    profile = UserProfileSerializer(required=False)
    academic_info = AcademicInfoSerializer(required=False)
    tracker_data = TrackerDataSerializer(required=False)
    
    class Meta:
        model = User
        fields = [
            'user_status', 'f_name', 'm_name', 'l_name', 'gender',
            'profile', 'academic_info', 'tracker_data'
        ]
    
    def update(self, instance, validated_data):
        # Update core user fields
        for attr, value in validated_data.items():
            if attr not in ['profile', 'academic_info', 'tracker_data']:
                setattr(instance, attr, value)
        instance.save()
        
        # Update profile
        if 'profile' in validated_data:
            profile_data = validated_data['profile']
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        # Update academic info
        if 'academic_info' in validated_data:
            academic_data = validated_data['academic_info']
            academic, created = AcademicInfo.objects.get_or_create(user=instance)
            for attr, value in academic_data.items():
                setattr(academic, attr, value)
            academic.save()
        
        # Update tracker data
        if 'tracker_data' in validated_data:
            tracker_data = validated_data['tracker_data']
            tracker, created = TrackerData.objects.get_or_create(user=instance)
            for attr, value in tracker_data.items():
                setattr(tracker, attr, value)
            tracker.save()
        
        return instance


class AlumniListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for alumni lists."""
    full_name = serializers.ReadOnlyField()
    email = serializers.CharField(source='profile.email', read_only=True)
    course = serializers.CharField(source='academic_info.course', read_only=True)
    year_graduated = serializers.IntegerField(source='academic_info.year_graduated', read_only=True)
    employment_status = serializers.CharField(source='tracker_data.q_employment_status', read_only=True)
    current_company = serializers.CharField(source='employment.company_name_current', read_only=True)
    current_position = serializers.CharField(source='employment.position_current', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'acc_username', 'full_name', 'email', 'course',
            'year_graduated', 'employment_status', 'current_company', 'current_position'
        ]


class AlumniStatsSerializer(serializers.Serializer):
    """Serializer for alumni statistics."""
    total_alumni = serializers.IntegerField()
    employed = serializers.IntegerField()
    unemployed = serializers.IntegerField()
    employment_rate = serializers.FloatField()
    job_aligned = serializers.IntegerField()
    pursuing_study = serializers.IntegerField()
    
    # Breakdown by year
    by_year = serializers.DictField(child=serializers.DictField(), required=False)
    
    # Breakdown by course
    by_course = serializers.DictField(child=serializers.DictField(), required=False)
    
    # Job alignment breakdown
    job_alignment_breakdown = serializers.DictField(child=serializers.IntegerField(), required=False)