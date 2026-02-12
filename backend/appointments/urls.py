from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('create/', views.appointment_create, name='appointment_create'),
    path('<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('<int:appointment_id>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('<int:appointment_id>/update-status/', views.appointment_update_status, name='appointment_update_status'),
    path('<int:appointment_id>/payment/', views.process_payment, name='process_payment'),
]
