from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment, Payment
from backend.services.models import Service
from backend.staff.models import Staff
from backend.schedules.models import Schedule


@login_required
def appointment_list(request):
    """Display user's appointments."""
    if request.user.role == 'Admin':
        appointments = Appointment.objects.all()
    else:
        appointments = Appointment.objects.filter(user=request.user)
    
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
        
        # Check if the schedule is available
        if not schedule.availability_status:
            messages.error(request, 'This time slot is not available.')
            return redirect('appointment_create')
        
        # Check for double booking
        if Appointment.objects.filter(schedule=schedule, status__in=['Pending', 'Confirmed']).exists():
            messages.error(request, 'This time slot is already booked.')
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
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
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


@login_required
def appointment_update_status(request, appointment_id):
    """Update appointment status (Admin/Staff only)."""
    if request.user.role not in ['Admin', 'Staff']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('appointment_list')
    
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
