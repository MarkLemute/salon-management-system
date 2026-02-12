from django.db import models
from backend.accounts.models import User
from backend.services.models import Service


class Staff(models.Model):
    """
    Model representing salon staff members.
    Links to User model for authentication.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    specialization = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'staff'
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff Members'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.specialization}"


class StaffService(models.Model):
    """
    Many-to-many relationship between Staff and Services.
    Defines which services each staff member can provide.
    """
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='staff_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_staff')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'staff_services'
        unique_together = ('staff', 'service')
        verbose_name = 'Staff Service'
        verbose_name_plural = 'Staff Services'
    
    def __str__(self):
        return f"{self.staff.user.username} - {self.service.name}"
