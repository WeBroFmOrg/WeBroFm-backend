import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webro_fm_backend.settings")
os.chdir("/var/www/webrofm/WeBroFm-backend")
django.setup()
from django.contrib.auth import authenticate
u = authenticate(phone_number="8888888888", password="Admin@12345")
print("Authenticated:", u)
if u:
    print("is_staff:", u.is_staff)
    print("is_superuser:", u.is_superuser)
