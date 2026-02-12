"""
User account validation utilities.
"""
import re
from django.core.exceptions import ValidationError
from .models import User


def validate_password_strength(password):
    """
    Validate password meets security requirements.
    
    Args:
        password: Password string to validate
        
    Raises:
        ValidationError: If password is weak
    """
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit.')


def validate_phone_number(phone):
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string to validate
        
    Raises:
        ValidationError: If phone format is invalid
    """
    if not phone:
        return  # Phone is optional
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it's a valid number (10-15 digits)
    if not re.match(r'^\+?\d{10,15}$', cleaned):
        raise ValidationError('Invalid phone number format. Use 10-15 digits.')


def validate_username_availability(username):
    """
    Validate that username is available.
    
    Args:
        username: Username to check
        
    Raises:
        ValidationError: If username already exists
    """
    if User.objects.filter(username=username).exists():
        raise ValidationError('Username already exists.')


def validate_email_availability(email):
    """
    Validate that email is available.
    
    Args:
        email: Email to check
        
    Raises:
        ValidationError: If email already exists
    """
    if User.objects.filter(email=email).exists():
        raise ValidationError('Email already exists.')
