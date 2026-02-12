from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Appointment, Payment
from backend.services.models import Service
from backend.staff.models import Staff
from backend.schedules.models import Schedule
from backend.accounts.decorators import staff_or_admin_required
from .validators import (
    validate_schedule_availability,
    validate_no_double_booking,
    validate_reschedule_eligibility
)


@login_required
def appointment_list(request):
    """Display user's appointments based on role."""
    if request.user.role == 'Admin':
        # Admin sees all appointments
        appointments = Appointment.objects.select_related(
            'user', 'service', 'staff__user', 'schedule__staff'
        ).all()
    elif request.user.role == 'Staff':
        # Staff sees appointments assigned to them
        try:
            staff_profile = Staff.objects.get(user=request.user)
            appointments = Appointment.objects.select_related(
                'user', 'service', 'staff__user', 'schedule__staff'
            ).filter(staff=staff_profile)
        except Staff.DoesNotExist:
            messages.error(request, 'Staff profile not found.')
            appointments = Appointment.objects.none()
    else:
        # Customers see their own appointments
        appointments = Appointment.objects.select_related(
            'service', 'staff__user', 'schedule__staff'
        ).filter(user=request.user)
    
    return render(request, 'appointments.html', {'appointments': appointments})


@login_required
def appointment_create(request):
    """Create a new appointment."""
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        staff_id = request.POST.get('staff_id')
        schedule_id = request.POST.get('schedule_id')
        notes = request.POST.get('notes', '')
        
        service = get_object_or_404(Service, id=service_id)
        staff = get_object_or_404(Staff, id=staff_id)
        schedule = get_object_or_404(Schedule, id=schedule_id)
        
        # Validate schedule availability
        try:
            validate_schedule_availability(schedule)
            validate_no_double_booking(schedule)
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('appointment_create')
        
        # Create appointment
        appointment = Appointment.objects.create(
            user=request.user,
            service=service,
            staff=staff,
            schedule=schedule,
            notes=notes
        )
        
        # Mark schedule as unavailable
        schedule.availability_status = False
        schedule.save()
        
        messages.success(request, 'Appointment booked successfully!')
        return redirect('appointment_detail', appointment_id=appointment.id)
    
    services = Service.objects.filter(is_active=True)
    return render(request, 'booking.html', {'services': services})


@login_required
def appointment_detail(request, appointment_id):
    """Display appointment details."""
    appointment = get_object_or_404(
        Appointment.objects.select_related(
            'user', 'service', 'staff__user', 'schedule__staff'
        ),
        id=appointment_id
    )
    
    # Check permission
    if request.user.role not in ['Admin', 'Staff'] and appointment.user != request.user:
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('appointment_list')
    
    return render(request, 'appointment_detail.html', {'appointment': appointment})


@login_required
def appointment_cancel(request, appointment_id):
    """Cancel an appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if request.user.role != 'Admin' and appointment.user != request.user:
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('appointment_list')
    
    if appointment.status == 'Cancelled':
        messages.warning(request, 'This appointment is already cancelled.')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    appointment.status = 'Cancelled'
    appointment.save()
    
    # Make schedule available again
    appointment.schedule.availability_status = True
    appointment.schedule.save()
    
    messages.success(request, 'Appointment cancelled successfully!')
    return redirect('appointment_list')


@staff_or_admin_required
def appointment_update_status(request, appointment_id):
    """Update appointment status (Admin/Staff only)."""
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        appointment.status = new_status
        appointment.save()
        
        messages.success(request, 'Appointment status updated successfully!')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    return render(request, 'update_status.html', {'appointment': appointment})


@login_required
def process_payment(request, appointment_id):
    """Process payment for an appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if appointment.user != request.user and request.user.role not in ['Admin', 'Staff']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('appointment_list')
    
    if hasattr(appointment, 'payment'):
        messages.warning(request, 'Payment already processed for this appointment.')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'Cash')
        
        Payment.objects.create(
            appointment=appointment,
            amount=appointment.service.price,
            payment_method=payment_method
        )
        
        # Update appointment status
        appointment.status = 'Confirmed'
        appointment.save()
        
        messages.success(request, 'Payment processed successfully!')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    return render(request, 'payment.html', {'appointment': appointment})


@login_required
def appointment_reschedule(request, appointment_id):
    """Reschedule an appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if request.user.role != 'Admin' and appointment.user != request.user:
        messages.error(request, 'You do not have permission to reschedule this appointment.')
        return redirect('appointment_list')
    
    if appointment.status in ['Cancelled', 'Completed']:
        messages.error(request, f'Cannot reschedule {appointment.status.lower()} appointments.')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        schedule_id = request.POST.get('schedule_id')
        
        staff = get_object_or_404(Staff, id=staff_id)
        new_schedule = get_object_or_404(Schedule, id=schedule_id)
        
        # Validate using validators
        try:
            validate_schedule_availability(new_schedule)
            validate_no_double_booking(new_schedule, exclude_appointment_id=appointment.id)
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('appointment_reschedule', appointment_id=appointment_id)
        
        # Make old schedule available
        old_schedule = appointment.schedule
        old_schedule.availability_status = True
        old_schedule.save()
        
        # Update appointment
        appointment.staff = staff
        appointment.schedule = new_schedule
        appointment.save()
        
        # Mark new schedule as unavailable
        new_schedule.availability_status = False
        new_schedule.save()
        
        messages.success(request, 'Appointment rescheduled successfully!')
        return redirect('appointment_detail', appointment_id=appointment.id)
    
    # Get available staff and schedules
    staff_members = Staff.objects.filter(is_available=True)
    
    context = {
        'appointment': appointment,
        'staff_members': staff_members,
    }
    return render(request, 'reschedule.html', context)
