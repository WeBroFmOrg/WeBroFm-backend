from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    role_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    permissions = models.JSONField(default=dict, blank=True,
        help_text='JSON object with resource: [actions] mapping')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')

    def __str__(self):
        return f"{self.role_name or 'Employee'} - {self.user.phone_number}"

    def has_permission(self, resource, action):
        if self.user.is_superuser:
            return True
        if not self.is_active:
            return False
        resource_perms = self.permissions.get(resource, [])
        return action in resource_perms
