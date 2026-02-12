from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Staff, StaffService
from backend.services.models import Service
from backend.accounts.decorators import admin_required


def staff_list(request):
    """Display all available staff members."""
    staff_members = Staff.objects.filter(is_available=True)
    return render(request, 'staff_list.html', {'staff_members': staff_members})


def staff_detail(request, staff_id):
    """Display staff member details and their services."""
    staff = get_object_or_404(Staff, id=staff_id)
    services = staff.staff_services.all()
    return render(request, 'staff_detail.html', {
        'staff': staff,
        'services': services
    })


@admin_required
def staff_create(request):
    """Create a new staff member (Admin only)."""
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        specialization = request.POST.get('specialization')
        bio = request.POST.get('bio')
        
        from backend.accounts.models import User
        user = get_object_or_404(User, id=user_id, role='Staff')
        
        # Check if user already has a staff profile
        if hasattr(user, 'staff_profile'):
            messages.error(request, 'This user already has a staff profile!')
            return redirect('staff_create')
        
        Staff.objects.create(
            user=user,
            specialization=specialization,
            bio=bio
        )
        
        messages.success(request, 'Staff member created successfully!')
        return redirect('staff_list')
    
    from backend.accounts.models import User
    # Only show users with Staff role who don't have a staff profile yet
    staff_users = User.objects.filter(role='Staff').exclude(staff_profile__isnull=False)
    return render(request, 'staff_form.html', {'staff_users': staff_users})


@admin_required
def assign_service(request, staff_id):
    """Assign a service to a staff member (Admin only)."""
    staff = get_object_or_404(Staff, id=staff_id)
    
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        service = get_object_or_404(Service, id=service_id)
        
        StaffService.objects.get_or_create(staff=staff, service=service)
        
        messages.success(request, 'Service assigned successfully!')
        return redirect('staff_detail', staff_id=staff_id)
    
    services = Service.objects.filter(is_active=True)
    assigned_services = staff.staff_services.values_list('service_id', flat=True)
    
    return render(request, 'assign_service.html', {
        'staff': staff,
        'services': services,
        'assigned_services': assigned_services
    })
