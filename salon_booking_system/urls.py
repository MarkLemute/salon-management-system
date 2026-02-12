"""
URL configuration for salon_booking_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('backend.accounts.urls')),
    path('services/', include('backend.services.urls')),
    path('staff/', include('backend.staff.urls')),
    path('appointments/', include('backend.appointments.urls')),
    path('schedules/', include('backend.schedules.urls')),
    path('api/', include('backend.api.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
