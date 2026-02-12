from django.contrib import admin
from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'time_slot', 'availability_status', 'created_at')
    list_filter = ('availability_status', 'date', 'created_at')
    search_fields = ('staff__user__username',)
    ordering = ('date', 'time_slot')
