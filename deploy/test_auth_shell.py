from django.contrib.auth import authenticate
u = authenticate(username="8888888888", password="Admin@12345")
print("Authenticated:", u)
if u:
    print("is_staff:", u.is_staff)
    print("is_superuser:", u.is_superuser)
else:
    from accounts.models import CustomUser
    print("Users in DB:", CustomUser.objects.count())
    u2 = CustomUser.objects.filter(phone_number="8888888888").first()
    if u2:
        print("Found user:", u2.phone_number, u2.is_staff, u2.is_superuser)
        print("Password check:", u2.check_password("Admin@12345"))
    else:
        print("User 8888888888 not found in DB")
