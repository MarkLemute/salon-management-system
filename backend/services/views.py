from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service


def service_list(request):
    """Display all active services."""
    services = Service.objects.filter(is_active=True)
    return render(request, 'services.html', {'services': services})


def service_detail(request, service_id):
    """Display service details."""
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'service_detail.html', {'service': service})


@login_required
def service_create(request):
    """Create a new service (Admin only)."""
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('service_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration = request.POST.get('duration')
        
        Service.objects.create(
            name=name,
            description=description,
            price=price,
            duration=duration
        )
        
        messages.success(request, 'Service created successfully!')
        return redirect('service_list')
    
    return render(request, 'service_form.html')


@login_required
def service_update(request, service_id):
    """Update an existing service (Admin only)."""
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('service_list')
    
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.description = request.POST.get('description')
        service.price = request.POST.get('price')
        service.duration = request.POST.get('duration')
        service.save()
        
        messages.success(request, 'Service updated successfully!')
        return redirect('service_list')
    
    return render(request, 'service_form.html', {'service': service})


@login_required
def service_delete(request, service_id):
    """Delete a service (Admin only)."""
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('service_list')
    
    service = get_object_or_404(Service, id=service_id)
    service.is_active = False
    service.save()
    
    messages.success(request, 'Service deleted successfully!')
    return redirect('service_list')
