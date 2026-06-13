from django.urls import path
from .views import SendOTPView, VerifyOTPView, UserProfileView

urlpatterns = [
    path('auth/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
]
