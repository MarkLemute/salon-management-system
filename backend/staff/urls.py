from django.urls import path
from . import views

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('<int:staff_id>/', views.staff_detail, name='staff_detail'),
    path('create/', views.staff_create, name='staff_create'),
    path('<int:staff_id>/assign-service/', views.assign_service, name='assign_service'),
]
