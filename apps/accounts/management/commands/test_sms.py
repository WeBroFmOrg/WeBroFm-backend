from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Test MSG91 configuration by sending a test OTP"

    def add_arguments(self, parser):
        parser.add_argument('phone_number', type=str, help='Phone number to send test OTP (e.g. 9999999999)')

    def handle(self, *args, **options):
        phone = options['phone_number']
        auth_key = settings.MSG91_AUTH_KEY
        template_id = settings.MSG91_TEMPLATE_ID
        country_code = getattr(settings, 'COUNTRY_CODE', '+91')

        self.stdout.write(f"MSG91_AUTH_KEY: {auth_key[:6]}...{auth_key[-4:]}")
        self.stdout.write(f"MSG91_TEMPLATE_ID: {template_id}")
        self.stdout.write(f"COUNTRY_CODE: {country_code}")
        self.stdout.write(f"Formatted phone: {country_code}{phone}")

        from services.sms_service import sms_service
        import random
        otp = f"{random.randint(100000, 999999)}"

        self.stdout.write(f"Sending OTP {otp} to {country_code}{phone}...")
        result = sms_service.send_otp(f"{country_code}{phone}", otp)

        if "error" in result:
            self.stdout.write(self.style.ERROR(f"FAILED: {result['error']}"))
            if "raw" in result:
                self.stdout.write(self.style.WARNING(f"Raw: {result['raw']}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"OTP sent! request_id: {result.get('request_id')}"))
