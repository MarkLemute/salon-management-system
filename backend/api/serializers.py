from rest_framework import serializers
from backend.accounts.models import User
from backend.services.models import Service
from backend.staff.models import Staff
from backend.schedules.models import Schedule
from backend.appointments.models import Appointment, Payment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone']
        extra_kwargs = {'password': {'write_only': True}}


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'duration', 'is_active']


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Staff
        fields = ['id', 'user', 'specialization', 'bio', 'is_available']


class ScheduleSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    
    class Meta:
        model = Schedule
        fields = ['id', 'staff', 'date', 'time_slot', 'availability_status']


class AppointmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    staff = StaffSerializer(read_only=True)
    schedule = ScheduleSerializer(read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'user', 'service', 'staff', 'schedule', 'status', 'notes', 'created_at']


class AppointmentCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    date = serializers.DateField()
    time_slot = serializers.CharField(max_length=50)
    notes = serializers.CharField(required=False, allow_blank=True)


class PaymentSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'appointment', 'amount', 'payment_date', 'payment_method', 'transaction_id']
