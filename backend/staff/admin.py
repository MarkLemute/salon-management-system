from django.contrib import admin
from .models import Staff, StaffService


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'is_available', 'created_at')
    list_filter = ('is_available', 'created_at')
    search_fields = ('user__username', 'user__email', 'specialization')


@admin.register(StaffService)
class StaffServiceAdmin(admin.ModelAdmin):
    list_display = ('staff', 'service', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('staff__user__username', 'service__name')
