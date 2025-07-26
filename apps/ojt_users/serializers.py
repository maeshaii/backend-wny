from rest_framework import serializers
from .models import OjtUser
from apps.shared.models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'user_id', 'acc_username', 'f_name', 'm_name', 'l_name', 
            'full_name', 'course', 'year_graduated', 'user_status', 
            'gender', 'email', 'phone_num', 'address'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.f_name} {obj.m_name or ''} {obj.l_name}".strip()

class OjtUserSerializer(serializers.ModelSerializer):
    """Serializer for OjtUser model"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    duration_days = serializers.ReadOnlyField()
    is_active_ojt = serializers.ReadOnlyField()
    
    class Meta:
        model = OjtUser
        fields = [
            'id', 'user', 'user_id', 'ojt_status', 'company_name', 
            'company_address', 'supervisor_name', 'supervisor_contact', 
            'supervisor_email', 'start_date', 'end_date', 'total_hours', 
            'position_title', 'department', 'stipend_amount', 
            'requirements_submitted', 'evaluation_score', 'remarks', 
            'created_at', 'updated_at', 'duration_days', 'is_active_ojt'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        # Check if OJT profile already exists
        if OjtUser.objects.filter(user=user).exists():
            raise serializers.ValidationError("OJT profile already exists for this user")
        
        validated_data['user'] = user
        return super().create(validated_data)

class OjtUserListSerializer(serializers.ModelSerializer):
    """Simplified serializer for OJT user list"""
    user_name = serializers.SerializerMethodField()
    ctu_id = serializers.CharField(source='user.acc_username', read_only=True)
    course = serializers.CharField(source='user.course', read_only=True)
    batch = serializers.CharField(source='user.year_graduated', read_only=True)
    
    class Meta:
        model = OjtUser
        fields = [
            'id', 'user_name', 'ctu_id', 'course', 'batch', 'ojt_status',
            'company_name', 'position_title', 'department', 'start_date',
            'end_date', 'total_hours', 'supervisor_name', 'stipend_amount',
            'requirements_submitted', 'evaluation_score', 'created_at'
        ]
    
    def get_user_name(self, obj):
        return f"{obj.user.f_name} {obj.user.m_name or ''} {obj.user.l_name}".strip()

class OjtUserStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating OJT status only"""
    class Meta:
        model = OjtUser
        fields = ['ojt_status', 'remarks']
    
    def validate_ojt_status(self, value):
        valid_statuses = [choice[0] for choice in OjtUser.OJT_STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        return value

class OjtUserEvaluationSerializer(serializers.ModelSerializer):
    """Serializer for updating evaluation details"""
    class Meta:
        model = OjtUser
        fields = ['evaluation_score', 'remarks', 'requirements_submitted']
    
    def validate_evaluation_score(self, value):
        if value is not None and (value < 0 or value > 5):
            raise serializers.ValidationError("Evaluation score must be between 0 and 5")
        return value 