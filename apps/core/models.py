from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils.translation import gettext_lazy as _


class EmployeeUser(models.Model):
    """Separate user model for admin employees only.
    Not linked to the public CustomUser model.
    Employees are created and managed solely through the admin panel.
    """
    phone_number = models.CharField(max_length=255, unique=True,
        help_text='Login identifier for the employee')
    password = models.CharField(max_length=255,
        help_text='Hashed password for employee login')
    full_name = models.CharField(max_length=255, blank=True)
    role_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    permissions = models.JSONField(default=dict, blank=True,
        help_text='JSON object with resource: [actions] mapping')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Employee User')
        verbose_name_plural = _('Employee Users')

    def __str__(self):
        return f"{self.role_name or 'Employee'} - {self.phone_number}"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def verify_password(self, raw_password):
        return check_password(raw_password, self.password)

    def has_permission(self, resource, action):
        if not self.is_active:
            return False
        resource_perms = self.permissions.get(resource, [])
        return action in resource_perms

    def has_any_permission(self):
        """Check if employee has any permissions at all."""
        for resource, actions in self.permissions.items():
            if actions:
                return True
        return False
