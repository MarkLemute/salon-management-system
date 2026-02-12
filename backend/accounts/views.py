from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import User
from .decorators import role_required, admin_required, staff_or_admin_required
from .validators import (
    validate_password_strength,
    validate_phone_number,
    validate_username_availability,
    validate_email_availability
)


def register_view(request):
    """Handle user registration."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        
        # Validate inputs
        try:
            if password != password2:
                raise ValidationError('Passwords do not match')
            
            validate_username_availability(username)
            validate_email_availability(email)
            validate_password_strength(password)
            validate_phone_number(phone)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone=phone,
                role='Customer'
            )
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
            
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'register.html')
    
    return render(request, 'register.html')


def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect based on user role
            if user.role == 'Admin':
                return redirect('admin_dashboard')
            elif user.role == 'Staff':
                return redirect('staff_dashboard')
            else:
                return redirect('customer_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')


@login_required
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def profile_view(request):
    """Display user profile."""
    return render(request, 'profile.html', {'user': request.user})


@login_required
def customer_dashboard(request):
    """Display customer dashboard with appointment statistics."""
    from backend.appointments.models import Appointment
    from backend.services.models import Service
    from django.utils import timezone
    from django.db.models import Count, Q
    
    today = timezone.now().date()
    
    # Get user's appointments
    appointments = Appointment.objects.filter(
        user=request.user,
        schedule__date__gte=today
    ).select_related('service', 'staff', 'schedule').order_by('schedule__date', 'schedule__time_slot')[:5]
    
    # Get appointment counts with single aggregated query (optimized)
    stats = Appointment.objects.filter(user=request.user).aggregate(
        upcoming=Count('id', filter=Q(
            schedule__date__gte=today,
            status__in=['Pending', 'Confirmed']
        )),
        completed=Count('id', filter=Q(status='Completed'))
    )
    
    upcoming_count = stats['upcoming']
    completed_count = stats['completed']
    total_services = Service.objects.count()
    
    context = {
        'user': request.user,
        'appointments': appointments,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'total_services': total_services,
    }
    
    return render(request, 'dashboard.html', context)


@admin_required
def admin_dashboard(request):
    """Display admin dashboard."""
    
    from backend.services.models import Service
    from backend.staff.models import Staff
    from backend.appointments.models import Appointment
    from backend.schedules.models import Schedule
    from django.db.models import Count
    
    # Get counts in a single query using aggregation where possible
    stats = {
        'total_services': Service.objects.count(),
        'total_staff': Staff.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_schedules': Schedule.objects.count(),
    }
    
    # Get recent appointments with optimized query
    recent_appointments = Appointment.objects.select_related(
        'user', 'service', 'staff__user', 'schedule__staff'
    ).all()[:10]
    
    context = {
        'user': request.user,
        **stats,
        'recent_appointments': recent_appointments
    }
    
    return render(request, 'admin_panel.html', context)


@role_required('Staff')
def staff_dashboard(request):
    """Display staff dashboard with their assignments and schedule."""
    from backend.staff.models import Staff
    from backend.appointments.models import Appointment
    from backend.schedules.models import Schedule
    from django.utils import timezone
    from django.db.models import Q, Count
    
    try:
        staff_profile = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found. Please contact admin.')
        return redirect('profile')
    
    # Get today's appointments for this staff member
    today = timezone.now().date()
    todays_appointments = Appointment.objects.filter(
        staff=staff_profile,
        schedule__date=today
    ).select_related('user', 'service', 'schedule').order_by('schedule__time_slot')
    
    # Get upcoming appointments (next 7 days)
    upcoming_appointments = Appointment.objects.filter(
        staff=staff_profile,
        schedule__date__gt=today,
        schedule__date__lte=today + timezone.timedelta(days=7),
        status__in=['Pending', 'Confirmed']
    ).select_related('user', 'service', 'schedule').order_by('schedule__date', 'schedule__time_slot')[:10]
    
    # Get stats with single aggregated query (optimized)
    stats = Appointment.objects.filter(staff=staff_profile).aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='Pending')),
        completed_today=Count('id', filter=Q(
            schedule__date=today,
            status='Completed'
        ))
    )
    
    total_appointments = stats['total']
    pending_appointments = stats['pending']
    completed_today = stats['completed_today']
    
    # Get staff schedule for the week
    week_schedules = Schedule.objects.filter(
        staff=staff_profile,
        date__gte=today,
        date__lte=today + timezone.timedelta(days=7)
    ).order_by('date', 'time_slot')
    
    # Group schedules by date for tabbed view
    from collections import defaultdict
    schedules_by_day = defaultdict(list)
    for schedule in week_schedules:
        schedules_by_day[schedule.date].append(schedule)
    
    # Convert to sorted list of tuples (date, schedules)
    schedules_by_day = sorted(schedules_by_day.items())
    
    context = {
        'user': request.user,
        'staff_profile': staff_profile,
        'todays_appointments': todays_appointments,
        'upcoming_appointments': upcoming_appointments,
        'total_appointments': total_appointments,
        'completed_today': completed_today,
        'pending_appointments': pending_appointments,
        'week_schedules': week_schedules,
        'schedules_by_day': schedules_by_day,
    }
    
    return render(request, 'staff_dashboard.html', context)
