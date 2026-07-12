from django.shortcuts import get_object_or_404

from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmployeeUser


class EmployeeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeUser
        fields = ('id', 'phone_number', 'full_name', 'role_name', 'is_active',
                  'permissions', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class EmployeeLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        phone_number = request.data.get('phone_number', '').strip()
        password = request.data.get('password', '')

        if not phone_number or not password:
            return Response({"error": "phone_number and password required"}, status=400)

        try:
            emp = EmployeeUser.objects.get(phone_number=phone_number, is_active=True)
        except EmployeeUser.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=401)

        if not emp.verify_password(password):
            return Response({"error": "Invalid credentials"}, status=401)

        refresh = RefreshToken()
        refresh['employee_id'] = emp.id
        refresh['phone_number'] = emp.phone_number
        refresh['is_employee'] = True

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'employee': {
                'id': emp.id,
                'phone_number': emp.phone_number,
                'full_name': emp.full_name,
                'role_name': emp.role_name,
                'is_active': emp.is_active,
                'permissions': emp.permissions,
            }
        })


class EmployeeListCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        employees = EmployeeUser.objects.all().order_by('-created_at')
        serializer = EmployeeUserSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):
        phone_number = request.data.get('phone_number', '').strip()
        password = request.data.get('password', '')

        if not phone_number:
            return Response({"error": "phone_number required"}, status=400)
        if not password:
            return Response({"error": "password required"}, status=400)
        if len(password) < 4:
            return Response({"error": "password must be at least 4 characters"}, status=400)
        if EmployeeUser.objects.filter(phone_number=phone_number).exists():
            return Response({"error": "Phone number already taken"}, status=400)

        emp = EmployeeUser(
            phone_number=phone_number,
            full_name=request.data.get('full_name', ''),
            role_name=request.data.get('role_name', ''),
            is_active=request.data.get('is_active', True),
            permissions=request.data.get('permissions', {}),
        )
        emp.set_password(password)
        emp.save()

        serializer = EmployeeUserSerializer(emp)
        return Response(serializer.data, status=201)


class EmployeeDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        emp = get_object_or_404(EmployeeUser, pk=pk)
        serializer = EmployeeUserSerializer(emp)
        return Response(serializer.data)

    def patch(self, request, pk):
        emp = get_object_or_404(EmployeeUser, pk=pk)
        writeable = ('full_name', 'role_name', 'is_active', 'permissions')
        for field in writeable:
            if field in request.data:
                setattr(emp, field, request.data[field])
        if 'password' in request.data and request.data['password']:
            raw = request.data['password']
            if len(raw) < 4:
                return Response({"error": "password must be at least 4 characters"}, status=400)
            emp.set_password(raw)
        emp.save()
        serializer = EmployeeUserSerializer(emp)
        return Response(serializer.data)

    def delete(self, request, pk):
        emp = get_object_or_404(EmployeeUser, pk=pk)
        emp.delete()
        return Response({"message": "Employee removed"})


class EmployeeToggleView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        emp = get_object_or_404(EmployeeUser, pk=pk)
        emp.is_active = not emp.is_active
        emp.save()
        return Response({"is_active": emp.is_active})


class AvailablePermissionsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        return Response({
            "shows": ["view", "create", "edit", "delete", "restore"],
            "episodes": ["view", "create", "edit", "delete", "restore"],
            "categories": ["view", "create", "edit", "delete"],
            "authors": ["view", "create", "edit", "delete"],
            "teasers": ["view", "create", "edit", "delete", "convert"],
            "users": ["view", "block"],
            "comments": ["view", "delete"],
            "reports": ["view", "resolve"],
            "feedback": ["view"],
            "stories": ["view", "approve", "reject"],
            "sponsorships": ["view", "approve", "reject", "expire"],
            "storage": ["view", "upload", "delete"],
            "dashboard": ["view"],
            "employees": ["view", "create", "edit", "delete"],
            "bin": ["view", "restore", "delete"],
        })
