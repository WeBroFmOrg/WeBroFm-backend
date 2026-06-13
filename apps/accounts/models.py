from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, **extra_fields):
        if not phone_number:
            raise ValueError(_('The Phone Number must be set'))
        
        user = self.model(phone_number=phone_number, **extra_fields)
        # Strictly No Passwords logic: set an unusable password
        user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, phone_number, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        # Superuser might need a password for admin site login, but let's keep it consistent
        # If the user wants admin access, they can use provide a password or we can add it later.
        user = self.create_user(phone_number, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        # For admin login, we might actually need a password. 
        # Let's set a default or allow setting one for superusers.
        user.set_password("admin123") # Default for dev
        user.save()
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True, verbose_name=_('Phone Number'))
    email = models.EmailField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Profile Completion Fields
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profiles/', blank=True, null=True)
    interests = models.ManyToManyField('content.Category', blank=True, related_name='interested_users')

    # OTP specific fields
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.phone_number
