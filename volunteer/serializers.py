from rest_framework import serializers
from django.contrib.auth.models import User
from .models import VolunteerProfile, Activity, Grade

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['name']

class VolunteerProfileSerializer(serializers.ModelSerializer):
    grade = GradeSerializer(read_only=True)
    level = serializers.CharField(read_only=True)

    class Meta:
        model = VolunteerProfile
        fields = ['student_id', 'total_hours', 'total_xp', 'gender', 'grade', 'level']

class UserSerializer(serializers.ModelSerializer):
    # 使用 source='volunteerprofile' 来反向查找关联的profile
    profile = VolunteerProfileSerializer(source='volunteerprofile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'profile']

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'