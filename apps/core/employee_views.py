from django.shortcuts import get_object_or_404

from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CustomUser
from accounts.serializers import UserSerializer
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'user', 'user_id', 'phone_number', 'role_name', 'is_active', 'permissions', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class EmployeeListCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        employees = Employee.objects.all().select_related('user').order_by('-created_at')
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        user = get_object_or_404(CustomUser, id=user_id)
        if hasattr(user, 'employee_profile'):
            return Response({"error": "User already an employee"}, status=400)

        employee = Employee.objects.create(
            user=user,
            role_name=request.data.get('role_name', ''),
            is_active=request.data.get('is_active', True),
            permissions=request.data.get('permissions', {}),
        )
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=201)


class EmployeeDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def patch(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        for field in ('role_name', 'is_active', 'permissions'):
            if field in request.data:
                setattr(employee, field, request.data[field])
        employee.save()
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def delete(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        employee.delete()
        return Response({"message": "Employee removed"})


class EmployeeToggleView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        employee.is_active = not employee.is_active
        employee.save()
        return Response({"is_active": employee.is_active})


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
