from django.conf import settings
from twilio.rest import Client


class TwilioService:
    def __init__(self):
        self.account_sid = settings.TWILIO_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        self._client = None

    @property
    def client(self):
        if self._client is None and self.account_sid and self.auth_token:
            self._client = Client(self.account_sid, self.auth_token)
        return self._client

    def send_otp(self, to_phone, otp):
        """Send OTP via Twilio SMS."""
        if self.client is None:
            return {"error": "Twilio not configured"}

        try:
            message = self.client.messages.create(
                to=to_phone,
                from_=self.phone_number,
                body=f"Your Webro FM OTP is: {otp}"
            )
            return {"sid": message.sid, "status": message.status}
        except Exception as e:
            return {"error": str(e)}


twilio_service = TwilioService()
