from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction

from backend.services.models import Service
from backend.staff.models import Staff
from backend.schedules.models import Schedule
from backend.appointments.models import Appointment, Payment
from backend.accounts.models import User

from .serializers import (
    ServiceSerializer,
    StaffSerializer,
    ScheduleSerializer,
    AppointmentSerializer,
    AppointmentCreateSerializer,
    PaymentSerializer,
    UserSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_overview(request):
    """API endpoint overview."""
    endpoints = {
        'services': '/api/services/',
        'staff': '/api/staff/',
        'schedules': '/api/schedules/',
        'appointments': '/api/appointments/',
        'book_appointment': '/api/appointments/book/',
        'user_register': '/api/users/register/',
    }
    return Response(endpoints)


# Services Endpoints
@api_view(['GET'])
@permission_classes([AllowAny])
def service_list_api(request):
    """Get all active services."""
    services = Service.objects.filter(is_active=True)
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def service_detail_api(request, service_id):
    """Get service details."""
    service = get_object_or_404(Service, id=service_id)
    serializer = ServiceSerializer(service)
    return Response(serializer.data)


# Staff Endpoints
@api_view(['GET'])
@permission_classes([AllowAny])
def staff_list_api(request):
    """Get all available staff members."""
    staff = Staff.objects.filter(is_available=True)
    serializer = StaffSerializer(staff, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def staff_detail_api(request, staff_id):
    """Get staff details."""
    staff = get_object_or_404(Staff, id=staff_id)
    serializer = StaffSerializer(staff)
    return Response(serializer.data)


# Schedules Endpoints
@api_view(['GET'])
@permission_classes([AllowAny])
def schedule_list_api(request):
    """Get available schedules."""
    staff_id = request.query_params.get('staff_id')
    date = request.query_params.get('date')
    
    schedules = Schedule.objects.filter(availability_status=True)
    
    if staff_id:
        schedules = schedules.filter(staff_id=staff_id)
    if date:
        schedules = schedules.filter(date=date)
    
    serializer = ScheduleSerializer(schedules, many=True)
    return Response(serializer.data)


# Appointments Endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_list_api(request):
    """Get user's appointments."""
    if request.user.role == 'Admin':
        appointments = Appointment.objects.all()
    else:
        appointments = Appointment.objects.filter(user=request.user)
    
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def appointment_book_api(request):
    """
    Book a new appointment.
    Expected JSON payload:
    {
        "user_id": 5,
        "service_id": 2,
        "staff_id": 1,
        "date": "2026-03-01",
        "time_slot": "10:00-11:00",
        "notes": "Optional notes"
    }
    """
    serializer = AppointmentCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        with transaction.atomic():
            # Get related objects
            user = get_object_or_404(User, id=data['user_id'])
            service = get_object_or_404(Service, id=data['service_id'])
            staff = get_object_or_404(Staff, id=data['staff_id'])
            
            # Get or validate schedule
            schedule = Schedule.objects.filter(
                staff=staff,
                date=data['date'],
                time_slot=data['time_slot']
            ).first()
            
            if not schedule:
                return Response(
                    {'error': 'Schedule not found for the selected date and time.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validate availability
            if not schedule.availability_status:
                return Response(
                    {'error': 'This time slot is not available.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check for double booking
            if Appointment.objects.filter(
                schedule=schedule,
                status__in=['Pending', 'Confirmed']
            ).exists():
                return Response(
                    {'error': 'This time slot is already booked.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create appointment
            appointment = Appointment.objects.create(
                user=user,
                service=service,
                staff=staff,
                schedule=schedule,
                notes=data.get('notes', '')
            )
            
            # Mark schedule as unavailable
            schedule.availability_status = False
            schedule.save()
            
            response_serializer = AppointmentSerializer(appointment)
            return Response(
                {
                    'message': 'Appointment booked successfully!',
                    'appointment': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_detail_api(request, appointment_id):
    """Get appointment details."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if request.user.role not in ['Admin', 'Staff'] and appointment.user != request.user:
        return Response(
            {'error': 'You do not have permission to view this appointment.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def appointment_update_status_api(request, appointment_id):
    """Update appointment status."""
    if request.user.role not in ['Admin', 'Staff']:
        return Response(
            {'error': 'You do not have permission to update appointment status.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    new_status = request.data.get('status')
    
    if new_status not in ['Pending', 'Confirmed', 'Completed', 'Cancelled']:
        return Response(
            {'error': 'Invalid status.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    appointment.status = new_status
    appointment.save()
    
    serializer = AppointmentSerializer(appointment)
    return Response({
        'message': 'Appointment status updated successfully!',
        'appointment': serializer.data
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def appointment_cancel_api(request, appointment_id):
    """Cancel an appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if request.user.role != 'Admin' and appointment.user != request.user:
        return Response(
            {'error': 'You do not have permission to cancel this appointment.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if appointment.status == 'Cancelled':
        return Response(
            {'error': 'This appointment is already cancelled.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    appointment.status = 'Cancelled'
    appointment.save()
    
    # Make schedule available again
    appointment.schedule.availability_status = True
    appointment.schedule.save()
    
    return Response({'message': 'Appointment cancelled successfully!'})


# User Registration
@api_view(['POST'])
@permission_classes([AllowAny])
def user_register_api(request):
    """Register a new user."""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not username or not email or not password:
        return Response(
            {'error': 'Username, email, and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='Customer'
    )
    
    serializer = UserSerializer(user)
    return Response(
        {
            'message': 'User registered successfully!',
            'user': serializer.data
        },
        status=status.HTTP_201_CREATED
    )
