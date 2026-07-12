from rest_framework.permissions import BasePermission


class HasEmployeePermission(BasePermission):
    """Check employee JWT has access to a specific resource+action.
    
    Expects request.auth to contain {'is_employee': True, 'employee_id': ...}.
    Usage: HasEmployeePermission(resource='shows', action='delete')
    """

    def __init__(self, resource=None, action=None):
        self.resource = resource
        self.action = action

    def has_permission(self, request, view):
        if not request.auth:
            return False
        if not request.auth.get('is_employee'):
            return False
        from .models import EmployeeUser
        try:
            emp = EmployeeUser.objects.get(
                pk=request.auth['employee_id'],
                is_active=True,
            )
        except (EmployeeUser.DoesNotExist, KeyError):
            return False
        return emp.has_permission(self.resource, self.action)

    def __call__(self):
        return self
