from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Service
from backend.accounts.decorators import admin_required
from backend.appointments.validators import validate_price, validate_duration


def service_list(request):
    """Display all active services."""
    services = Service.objects.filter(is_active=True)
    return render(request, 'services.html', {'services': services})


def service_detail(request, service_id):
    """Display service details."""
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'service_detail.html', {'service': service})


@admin_required
def service_create(request):
    """Create a new service (Admin only)."""
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration = request.POST.get('duration')
        
        try:
            # Validate inputs
            validate_price(price)
            validate_duration(duration)
            
            Service.objects.create(
                name=name,
                description=description,
                price=price,
                duration=duration
            )
            
            messages.success(request, 'Service created successfully!')
            return redirect('service_list')
            
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'service_form.html')
    
    return render(request, 'service_form.html')


@admin_required
def service_update(request, service_id):
    """Update an existing service (Admin only)."""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        try:
            price = request.POST.get('price')
            duration = request.POST.get('duration')
            
            # Validate inputs
            validate_price(price)
            validate_duration(duration)
            
            service.name = request.POST.get('name')
            service.description = request.POST.get('description')
            service.price = price
            service.duration = duration
            service.is_active = request.POST.get('is_active') == 'on'
            service.save()
            
            messages.success(request, 'Service updated successfully!')
            return redirect('service_list')
            
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'service_form.html', {'service': service})
    
    return render(request, 'service_form.html', {'service': service})


@admin_required
def service_delete(request, service_id):
    """Delete a service (Admin only)."""
    
    service = get_object_or_404(Service, id=service_id)
    service.is_active = False
    service.save()
    
    messages.success(request, 'Service deleted successfully!')
    return redirect('service_list')
