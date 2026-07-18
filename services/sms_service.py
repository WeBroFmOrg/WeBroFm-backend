import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SMS91Service:
    def __init__(self):
        self.auth_key = settings.MSG91_AUTH_KEY
        self.template_id = settings.MSG91_TEMPLATE_ID

    def send_otp(self, phone_number, otp):
        """Send OTP via MSG91 with multiple fallback approaches."""
        endpoints = [
            "https://api.msg91.com/api/v5/otp",
            "https://control.msg91.com/api/v5/otp",
            "https://api.msg91.com/api/sendotp.php",
        ]

        last_error = None
        for url in endpoints:
            result = self._try_send(url, phone_number, otp)
            if "error" not in result:
                return result
            last_error = result

        return last_error

    def _try_send(self, url, phone_number, otp):
        try:
            # Approach 1: GET with query params
            response = requests.get(
                url,
                params={
                    "authkey": self.auth_key,
                    "template_id": self.template_id,
                    "mobile": phone_number,
                    "otp": otp,
                    "realTimeResponse": 1,
                },
                timeout=10,
            )
            data = self._parse_response(response, url)
            if data.get("type") == "success":
                return {"request_id": data.get("request_id"), "status": "sent"}
            if "Invalid authkey" not in response.text:
                return {"error": data.get("message", "MSG91 error"), "raw": response.text}

            # Approach 2: POST with auth in header
            headers = {"X-API-Key": self.auth_key}
            response = requests.post(
                url if "sendotp" not in url else url,
                data={
                    "authkey": self.auth_key,
                    "template_id": self.template_id,
                    "mobile": phone_number,
                    "otp": otp,
                    "realTimeResponse": 1,
                },
                headers=headers,
                timeout=10,
            )
            data = self._parse_response(response, url)
            if data.get("type") == "success":
                return {"request_id": data.get("request_id"), "status": "sent"}
            return {"error": data.get("message", "MSG91 error"), "raw": response.text}

        except requests.Timeout:
            return {"error": f"Timeout for {url}"}
        except Exception as e:
            return {"error": f"{e}"}

    def _parse_response(self, response, url):
        logger.info(f"MSG91 [{url}] status={response.status_code}: {response.text[:500]}")
        try:
            return response.json()
        except Exception:
            return {"type": "error", "message": response.text}


sms_service = SMS91Service()
