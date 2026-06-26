import requests
from django.conf import settings


class SMS91Service:
    def __init__(self):
        self.auth_key = settings.MSG91_AUTH_KEY
        self.template_id = settings.MSG91_TEMPLATE_ID

    def send_otp(self, phone_number, otp):
        """Send OTP via MSG91."""
        try:
            response = requests.post(
                "https://api.msg91.com/api/v5/otp",
                params={
                    "authkey": self.auth_key,
                    "template_id": self.template_id,
                    "mobile": phone_number,
                    "otp": otp,
                    "realTimeResponse": 1,
                },
                timeout=10,
            )
            data = response.json()
            if data.get("type") == "success":
                return {"request_id": data.get("request_id"), "status": "sent"}
            return {"error": data.get("message", "MSG91 error")}
        except Exception as e:
            return {"error": str(e)}


sms_service = SMS91Service()
