from accounts.models import CustomUser
u = CustomUser.objects.get(phone_number="8888888888")
u.set_password("Admin@12345")
u.save()
print("Password reset done")
from django.contrib.auth import authenticate
u2 = authenticate(username="8888888888", password="Admin@12345")
print("Now authenticated:", u2)
