from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Schedule
from backend.staff.models import Staff


def schedule_list(request):
    """Display available schedules."""
    today = timezone.now().date()
    staff_id = request.GET.get('staff_id')
    date = request.GET.get('date')
    
    schedules = Schedule.objects.filter(
        date__gte=today,
        availability_status=True
    )
    
    if staff_id:
        schedules = schedules.filter(staff_id=staff_id)
    
    if date:
        schedules = schedules.filter(date=date)
    
    staff_members = Staff.objects.filter(is_available=True)
    
    return render(request, 'schedule_list.html', {
        'schedules': schedules,
        'staff_members': staff_members
    })


@login_required
def schedule_create(request):
    """Create a new schedule (Admin only)."""
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('schedule_list')
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        
        staff = get_object_or_404(Staff, id=staff_id)
        
        # Check if schedule already exists
        if Schedule.objects.filter(staff=staff, date=date, time_slot=time_slot).exists():
            messages.error(request, 'This schedule already exists.')
            return redirect('schedule_create')
        
        Schedule.objects.create(
            staff=staff,
            date=date,
            time_slot=time_slot
        )
        
        messages.success(request, 'Schedule created successfully!')
        return redirect('schedule_list')
    
    staff_members = Staff.objects.filter(is_available=True)
    
    # Generate time slots (9 AM to 6 PM, 1-hour intervals)
    time_slots = []
    start_hour = 9
    end_hour = 18
    for hour in range(start_hour, end_hour):
        time_slot = f"{hour:02d}:00-{hour+1:02d}:00"
        time_slots.append(time_slot)
    
    return render(request, 'schedule_form.html', {
        'staff_members': staff_members,
        'time_slots': time_slots
    })


@login_required
def schedule_bulk_create(request):
    """Create schedules in bulk for a staff member (Admin only)."""
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('schedule_list')
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        time_slots = request.POST.getlist('time_slots')
        
        staff = get_object_or_404(Staff, id=staff_id)
        
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Generate schedules for the date range
        current_date = start
        created_count = 0
        
        while current_date <= end:
            for time_slot in time_slots:
                if not Schedule.objects.filter(
                    staff=staff,
                    date=current_date,
                    time_slot=time_slot
                ).exists():
                    Schedule.objects.create(
                        staff=staff,
                        date=current_date,
                        time_slot=time_slot
                    )
                    created_count += 1
            
            current_date += timedelta(days=1)
        
        messages.success(request, f'{created_count} schedules created successfully!')
        return redirect('schedule_list')
    
    staff_members = Staff.objects.filter(is_available=True)
    
    # Generate time slots
    time_slots = []
    for hour in range(9, 18):
        time_slot = f"{hour:02d}:00-{hour+1:02d}:00"
        time_slots.append(time_slot)
    
    return render(request, 'schedule_bulk_form.html', {
        'staff_members': staff_members,
        'time_slots': time_slots
    })


@login_required
def schedule_delete(request, schedule_id):
    """Delete a schedule (Admin only)."""
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('schedule_list')
    
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    # Check if schedule has appointments
    if hasattr(schedule, 'appointments') and schedule.appointments.exists():
        messages.error(request, 'Cannot delete a schedule with existing appointments.')
        return redirect('schedule_list')
    
    schedule.delete()
    messages.success(request, 'Schedule deleted successfully!')
    return redirect('schedule_list')
