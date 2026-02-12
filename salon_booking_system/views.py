from django.shortcuts import render
from backend.services.models import Service


def home_view(request):
    """Display home page with featured services."""
    services = Service.objects.filter(is_active=True)[:4]  # Show first 4 services
    return render(request, 'home.html', {'services': services})
