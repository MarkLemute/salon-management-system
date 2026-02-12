from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from backend.services.models import Service
from backend.staff.models import Staff
from backend.schedules.models import Schedule
from backend.appointments.models import Appointment, Payment
from backend.accounts.models import User
from backend.appointments.validators import (
    validate_schedule_availability,
    validate_no_double_booking
)

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
        'reschedule_appointment': '/api/appointments/<id>/reschedule/',
        'cancel_appointment': '/api/appointments/<id>/cancel/',
        'staff_service_assign': '/api/staff-services/assign/',
        'staff_services_list': '/api/staff/<id>/services/',
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
    """
    Get all available staff members.
    Filter by service_id if provided in query parameters.
    """
    service_id = request.query_params.get('service_id')
    
    staff = Staff.objects.filter(is_available=True)
    
    # Filter by service if service_id is provided
    if service_id:
        # Optimized: Use JOIN instead of subquery
        staff = staff.filter(staff_services__service_id=service_id).distinct()
    
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
        appointments = Appointment.objects.select_related(
            'user', 'service', 'staff__user', 'schedule__staff'
        ).all()
    else:
        appointments = Appointment.objects.select_related(
            'service', 'staff__user', 'schedule__staff'
        ).filter(user=request.user)
    
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
            try:
                validate_schedule_availability(schedule)
                validate_no_double_booking(schedule)
            except DjangoValidationError as e:
                return Response(
                    {'error': str(e)},
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
    appointment = get_object_or_404(
        Appointment.objects.select_related(
            'user', 'service', 'staff__user', 'schedule__staff'
        ),
        id=appointment_id
    )
    
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


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def appointment_reschedule_api(request, appointment_id):
    """
    Reschedule an appointment.
    Expected JSON payload:
    {
        "staff_id": 1,
        "date": "2026-03-15",
        "time_slot": "14:00-15:00"
    }
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if request.user.role != 'Admin' and appointment.user != request.user:
        return Response(
            {'error': 'You do not have permission to reschedule this appointment.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if appointment.status in ['Cancelled', 'Completed']:
        return Response(
            {'error': f'Cannot reschedule {appointment.status.lower()} appointments.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    staff_id = request.data.get('staff_id')
    date = request.data.get('date')
    time_slot = request.data.get('time_slot')
    
    if not all([staff_id, date, time_slot]):
        return Response(
            {'error': 'staff_id, date, and time_slot are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic():
            staff = get_object_or_404(Staff, id=staff_id)
            
            # Get new schedule
            new_schedule = Schedule.objects.filter(
                staff=staff,
                date=date,
                time_slot=time_slot
            ).first()
            
            if not new_schedule:
                return Response(
                    {'error': 'Schedule not found for the selected date and time.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validate availability
            try:
                validate_schedule_availability(new_schedule)
                validate_no_double_booking(new_schedule, exclude_appointment_id=appointment.id)
            except DjangoValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Make old schedule available
            old_schedule = appointment.schedule
            old_schedule.availability_status = True
            old_schedule.save()
            
            # Update appointment
            appointment.staff = staff
            appointment.schedule = new_schedule
            appointment.save()
            
            # Mark new schedule as unavailable
            new_schedule.availability_status = False
            new_schedule.save()
            
            serializer = AppointmentSerializer(appointment)
            return Response(
                {
                    'message': 'Appointment rescheduled successfully!',
                    'appointment': serializer.data
                },
                status=status.HTTP_200_OK
            )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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


# Staff-Service Assignment Endpoints
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def staff_service_assign_api(request):
    """
    Assign a service to a staff member.
    Expected JSON payload:
    {
        "staff_id": 1,
        "service_id": 2
    }
    """
    if request.user.role != 'Admin':
        return Response(
            {'error': 'Only administrators can assign services to staff.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    staff_id = request.data.get('staff_id')
    service_id = request.data.get('service_id')
    
    if not staff_id or not service_id:
        return Response(
            {'error': 'staff_id and service_id are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    staff = get_object_or_404(Staff, id=staff_id)
    service = get_object_or_404(Service, id=service_id)
    
    from backend.staff.models import StaffService
    
    # Check if already assigned
    if StaffService.objects.filter(staff=staff, service=service).exists():
        return Response(
            {'error': 'This service is already assigned to the staff member.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    staff_service = StaffService.objects.create(staff=staff, service=service)
    
    return Response(
        {
            'message': 'Service assigned to staff successfully!',
            'staff': staff.user.username,
            'service': service.name
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def staff_service_remove_api(request, staff_id, service_id):
    """Remove a service assignment from a staff member."""
    if request.user.role != 'Admin':
        return Response(
            {'error': 'Only administrators can remove service assignments.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    from backend.staff.models import StaffService
    
    staff_service = get_object_or_404(StaffService, staff_id=staff_id, service_id=service_id)
    staff_service.delete()
    
    return Response({'message': 'Service assignment removed successfully!'})


@api_view(['GET'])
@permission_classes([AllowAny])
def staff_services_list_api(request, staff_id):
    """Get all services assigned to a staff member."""
    staff = get_object_or_404(Staff, id=staff_id)
    from backend.staff.models import StaffService
    
    staff_services = StaffService.objects.filter(staff=staff).select_related('service')
    services = [ss.service for ss in staff_services]
    
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)
