from django.db import models
from backend.accounts.models import User
from backend.services.models import Service
from backend.staff.models import Staff
from backend.schedules.models import Schedule


class Appointment(models.Model):
    """
    Model representing an appointment booking.
    """
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='appointments')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='appointments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointments'
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.service.name} - {self.schedule.date} {self.schedule.time_slot}"


class Payment(models.Model):
    """
    Model representing payment for an appointment.
    """
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, default='Cash')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"Payment for Appointment #{self.appointment.id} - ${self.amount}"
