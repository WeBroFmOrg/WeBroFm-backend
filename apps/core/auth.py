from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken


class EmployeeUserProxy:
    """Virtual user object that passes IsAdminUser (is_staff=True) for employee JWT."""
    is_authenticated = True
    is_active = True
    is_staff = True
    is_superuser = False

    def __init__(self, employee):
        self.pk = -employee.id
        self.id = -employee.id
        self.phone_number = employee.phone_number
        self.full_name = employee.full_name
        self._employee = employee

    def __str__(self):
        return f"Employee({self.phone_number})"

    def __repr__(self):
        return f"<EmployeeUserProxy: {self.phone_number}>"


class EmployeeJWTAuthentication(BaseAuthentication):
    """Authenticate employee JWT tokens (with is_employee claim).
    Falls back to standard JWTAuthentication for superuser tokens.
    """

    def authenticate(self, request):
        jwt_auth = JWTAuthentication()
        header = jwt_auth.get_header(request)
        if header is None:
            return None

        raw_token = jwt_auth.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = jwt_auth.get_validated_token(raw_token)
        except InvalidToken:
            return None

        # Check if this is an employee token
        if validated_token.get('is_employee'):
            employee_id = validated_token.get('employee_id')
            if employee_id is None:
                raise AuthenticationFailed('Invalid employee token: missing employee_id')

            from .models import EmployeeUser
            try:
                emp = EmployeeUser.objects.get(pk=employee_id, is_active=True)
            except EmployeeUser.DoesNotExist:
                raise AuthenticationFailed('Employee not found or inactive')

            return (EmployeeUserProxy(emp), validated_token)

        # Fall back to standard user lookup for superuser tokens
        try:
            return jwt_auth.authenticate(request)
        except InvalidToken:
            return None
