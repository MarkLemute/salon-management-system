"""
Validation utilities for appointment booking system.
Centralizes common validation logic to reduce code duplication.
"""
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Appointment


def validate_schedule_availability(schedule):
    """
    Validate that a schedule is available for booking.
    
    Args:
        schedule: Schedule instance to validate
        
    Raises:
        ValidationError: If schedule is not available
    """
    if not schedule.availability_status:
        raise ValidationError('This time slot is not available.')


def validate_no_double_booking(schedule, exclude_appointment_id=None):
    """
    Validate that a schedule doesn't have conflicting appointments.
    
    Args:
        schedule: Schedule instance to check
        exclude_appointment_id: Optional appointment ID to exclude from check (for rescheduling)
        
    Raises:
        ValidationError: If schedule is already booked
    """
    query = Q(schedule=schedule, status__in=['Pending', 'Confirmed'])
    
    if exclude_appointment_id:
        query &= ~Q(id=exclude_appointment_id)
    
    if Appointment.objects.filter(query).exists():
        raise ValidationError('This time slot is already booked.')


def validate_appointment_status_change(appointment, new_status):
    """
    Validate that an appointment status change is allowed.
    
    Args:
        appointment: Appointment instance
        new_status: New status to set
        
    Raises:
        ValidationError: If status change is not allowed
    """
    if appointment.status == 'Cancelled' and new_status != 'Cancelled':
        raise ValidationError('Cannot change status of cancelled appointment.')
    
    if appointment.status == 'Completed' and new_status not in ['Completed', 'Cancelled']:
        raise ValidationError('Cannot change status of completed appointment.')


def validate_reschedule_eligibility(appointment):
    """
    Validate that an appointment can be rescheduled.
    
    Args:
        appointment: Appointment instance
        
    Raises:
        ValidationError: If appointment cannot be rescheduled
    """
    if appointment.status in ['Cancelled', 'Completed']:
        raise ValidationError(f'Cannot reschedule {appointment.status.lower()} appointments.')


def validate_price(price):
    """
    Validate that a price is valid.
    
    Args:
        price: Price value to validate
        
    Raises:
        ValidationError: If price is invalid
    """
    try:
        price_decimal = float(price)
        if price_decimal < 0:
            raise ValidationError('Price cannot be negative.')
        if price_decimal > 10000:
            raise ValidationError('Price cannot exceed $10,000.')
    except (TypeError, ValueError):
        raise ValidationError('Invalid price format.')


def validate_duration(duration):
    """
    Validate that a service duration is reasonable.
    
    Args:
        duration: Duration in minutes
        
    Raises:
        ValidationError: If duration is invalid
    """
    try:
        duration_int = int(duration)
        if duration_int < 5:
            raise ValidationError('Duration must be at least 5 minutes.')
        if duration_int > 480:  # 8 hours
            raise ValidationError('Duration cannot exceed 8 hours.')
    except (TypeError, ValueError):
        raise ValidationError('Invalid duration format.')
