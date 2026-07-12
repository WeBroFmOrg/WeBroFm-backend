from rest_framework.permissions import BasePermission
from .models import Employee


class EmployeePermission(BasePermission):
    """Check employee has access to a specific resource+action.
    
    Usage: EmployeePermission(resource='shows', action='delete')
    For superuser, always returns True.
    """

    def __init__(self, resource=None, action=None):
        self.resource = resource
        self.action = action

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if not self.resource or not self.action:
            return request.user.is_staff
        try:
            employee = request.user.employee_profile
            return employee.has_permission(self.resource, self.action)
        except Employee.DoesNotExist:
            return False

    def __call__(self):
        return self
