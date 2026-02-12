from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for salon booking system.
    Extends Django's AbstractUser with additional fields.
    """
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Staff', 'Staff'),
        ('Customer', 'Customer'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Customer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.role})"
