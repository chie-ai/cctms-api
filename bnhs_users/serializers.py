from rest_framework import serializers
from .models import BNHSUser, UserNumber, Grade, HealthCareService, UserProfile
from covid19_case_records.models import *
from covid19_case_records.serializers import *
from django.core.exceptions import ValidationError

class BNHSUsersSerializer(serializers.ModelSerializer):
    user_number = serializers.StringRelatedField(read_only=True) # Use this sript to get the 'user_number' field only by related_name from model
    user_profile = serializers.SerializerMethodField() # Use this sript to get the 'user_number' field only by related_name from model
    grade_level = serializers.StringRelatedField(read_only=True) # Use this sript to get the 'grade_level/level' field only by related_name from model
    health_care_service = serializers.StringRelatedField(read_only=True) # Use this sript to get the 'health_center_service' field only by related_name from model
    vaccination_record = serializers.StringRelatedField(many=True, read_only=True) # Use this sript to get the 'health_center_service' field only by related_name from model

    ################################################################################################################################################################################
    covid19_main_status = serializers.SerializerMethodField() # Use this script to get single data from an array via method field
    # covid19_status = CovidCaseRecordSerializer(many=True, read_only=True) # Use this script to get the 'covid_status' related_name object of model 'covid119_case_records'
    covid19_status = serializers.StringRelatedField(many=True, read_only=True) # Use this script to get the 'covid_status' only by related_name from model 'covid119_case_records'
    ################################################################################################################################################################################

    def get_user_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user_id=obj.pk)
            serializer = UserProfileSerializer(profile)
            return serializer.data
        except UserProfile.DoesNotExist:
            queryset = UserProfile.objects.none()
            serializer = UserProfileSerializer(queryset)
            return serializer.data
            
    def get_covid19_main_status(self, obj):
        query = CovidCaseRecord.objects.filter(user_id=obj.pk)[:1]
        serializer = CovidCaseRecordSerializer(query, many=True)
        return serializer.data

    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = BNHSUser
        fields: [
            'username', 'first_name', 'middle_name', 'last_name',
            'sex', 'address', 'contact_number', 'email', 'usertype', 'password', 'password2'
        ]
        extra_kwargs = {'password': {'write_only': True}}
        exclude = ['is_active', 'is_admin']

    def save(self):
        user = BNHSUser(
            username=self.validated_data['username'],
            first_name=self.validated_data['first_name'],
            middle_name=self.validated_data['middle_name'],
            last_name=self.validated_data['last_name'],
            sex=self.validated_data['sex'],
            address=self.validated_data['address'],
            contact_number=self.validated_data['contact_number'],
            email=self.validated_data['email'],
            usertype=self.validated_data['usertype']
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        # if password != password2:
        #     raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.is_admin = False
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    user_number = serializers.StringRelatedField(read_only=True) # Use this sript to get the 'user_number' field only by related_name from model
    user_profile = serializers.SerializerMethodField() # Use this sript to get the 'user_number' field only by related_name from model
    grade_level = serializers.StringRelatedField(read_only=True) # Use this sript to get the 'grade_level/level' field only by related_name from model
    covid19_status = CovidCaseRecordSerializer(many=True, read_only=True) # Use this script to get the 'covid_status' related_name object of model
    health_care_service = serializers.StringRelatedField(read_only=True) # Use this sript to get the 'health_center_service' field only by related_name from model

    def get_user_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user_id=obj.pk)
            serializer = UserProfileSerializer(profile)
            return serializer.data
        except UserProfile.DoesNotExist:
            queryset = UserProfile.objects.none()
            serializer = UserProfileSerializer(queryset)
            return serializer.data

    class Meta:
        model = BNHSUser
        fields: [
            'username', 'first_name', 'middle_name', 'last_name',
            'sex', 'address', 'contact_number', 'email', 'usertype', 'password', 'password2'
        ]
        exclude = ['is_active', 'is_admin', 'password']

class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = BNHSUser
        fields: [
            'username', 'first_name', 'middle_name', 'last_name',
            'sex', 'address', 'contact_number', 'email', 'usertype', 'password', 'password2'
        ]
        exclude = ['is_active', 'is_admin', 'password']

class UserNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNumber
        fields = ['user_id', 'user_number']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user_id', 'profile_file']

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['student_id', 'level']

    # def save(self):
    #     student_grade = Grade.objects.create(
    #         student_id=self.context.get('foreignKey'),
    #         grade=self.validated_data['level']
    #     )

class HealthCareServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCareService
        fields = ['user_id', 'health_care_service', 'created_at']

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"}, required=True)
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'current_password': 'Does not match'})
        return value
