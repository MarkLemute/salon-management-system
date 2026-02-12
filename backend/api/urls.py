from django.urls import path
from . import views

urlpatterns = [
    # API Overview
    path('', views.api_overview, name='api_overview'),
    
    # Services
    path('services/', views.service_list_api, name='service_list_api'),
    path('services/<int:service_id>/', views.service_detail_api, name='service_detail_api'),
    
    # Staff
    path('staff/', views.staff_list_api, name='staff_list_api'),
    path('staff/<int:staff_id>/', views.staff_detail_api, name='staff_detail_api'),
    
    # Schedules
    path('schedules/', views.schedule_list_api, name='schedule_list_api'),
    
    # Appointments
    path('appointments/', views.appointment_list_api, name='appointment_list_api'),
    path('appointments/book/', views.appointment_book_api, name='appointment_book_api'),
    path('appointments/<int:appointment_id>/', views.appointment_detail_api, name='appointment_detail_api'),
    path('appointments/<int:appointment_id>/update-status/', views.appointment_update_status_api, name='appointment_update_status_api'),
    path('appointments/<int:appointment_id>/cancel/', views.appointment_cancel_api, name='appointment_cancel_api'),
    
    # User Registration
    path('users/register/', views.user_register_api, name='user_register_api'),
]
