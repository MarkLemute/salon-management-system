from django.contrib import admin
from .models import Appointment, Payment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service', 'staff', 'schedule', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'service__name', 'staff__user__username')
    ordering = ('-created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'amount', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('appointment__user__username', 'transaction_id')
    ordering = ('-payment_date',)
