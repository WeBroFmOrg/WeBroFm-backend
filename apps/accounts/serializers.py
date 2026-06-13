from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class OTPSendSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'email', 'full_name', 'date_of_birth', 'profile_picture', 'interests', 'date_joined')
        read_only_fields = ('id', 'phone_number', 'date_joined')
