from django.urls import path
from . import views

urlpatterns = [
    path('', views.schedule_list, name='schedule_list'),
    path('create/', views.schedule_create, name='schedule_create'),
    path('bulk-create/', views.schedule_bulk_create, name='schedule_bulk_create'),
    path('<int:schedule_id>/delete/', views.schedule_delete, name='schedule_delete'),
]
