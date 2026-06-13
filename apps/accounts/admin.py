from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'full_name', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('phone_number', 'full_name')
    list_filter = ('is_active', 'is_staff')
    ordering = ('-date_joined',)
