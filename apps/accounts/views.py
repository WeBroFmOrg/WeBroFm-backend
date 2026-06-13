import random
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import OTPSendSerializer, OTPVerifySerializer, UserSerializer
from services.twilio_service import twilio_service

User = get_user_model()


class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']

        # Find or create user
        user, created = User.objects.get_or_create(phone_number=phone_number)

        # Dev/Dummy OTP logic (mirrors old PHP behavior)
        dummy_phone = settings.DUMMY_PHONE
        dummy_otp = settings.DUMMY_OTP
        enable_dev = settings.ENABLE_DEV_LOGIN

        if enable_dev and phone_number == dummy_phone:
            user.otp_code = dummy_otp
            user.otp_expiry = timezone.now() + timedelta(days=365)
            user.save()
            return Response({
                "message": "OTP sent successfully",
                "otp": dummy_otp
            }, status=status.HTTP_200_OK)

        # Normal OTP generation - re-use existing OTP if still valid
        if user.otp_code and user.otp_expiry and user.otp_expiry > timezone.now():
            otp_code = user.otp_code
        else:
            otp_code = f"{random.randint(100000, 999999)}"
            user.otp_code = otp_code
            user.otp_expiry = timezone.now() + timedelta(minutes=5)
            user.save()

        # Send via Twilio
        formatted_phone = f"{settings.DUMMY_COUNTRY_CODE}{phone_number}"
        result = twilio_service.send_otp(formatted_phone, otp_code)

        if "error" in result:
            print(f"Twilio error: {result['error']}")

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Dev/Dummy OTP verification (skip expiry for dummy)
        dummy_phone = settings.DUMMY_PHONE
        dummy_otp = settings.DUMMY_OTP
        enable_dev = settings.ENABLE_DEV_LOGIN

        if enable_dev and phone_number == dummy_phone:
            if otp_code == dummy_otp:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'OTP verified successfully',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # Normal OTP verification
        if not user.otp_code or not user.otp_expiry:
            return Response({"error": "OTP not set"}, status=status.HTTP_400_BAD_REQUEST)

        if user.otp_expiry < timezone.now():
            return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        if user.otp_code != otp_code:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # Clear OTP fields
        user.otp_code = None
        user.otp_expiry = None
        user.save()

        # Generate JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'OTP verified successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
