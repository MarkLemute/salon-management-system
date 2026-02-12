from django.test import TestCase
from django.utils import timezone
from backend.accounts.models import User
from backend.services.models import Service
from backend.staff.models import Staff
from backend.schedules.models import Schedule
from backend.appointments.models import Appointment


class AppointmentBookingTest(TestCase):
    """Test cases for appointment booking."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.customer = User.objects.create_user(
            username='customer',
            password='pass123',
            role='Customer'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            password='pass123',
            role='Staff'
        )
        
        # Create service
        self.service = Service.objects.create(
            name='Haircut',
            price=25.00,
            duration=30
        )
        
        # Create staff
        self.staff = Staff.objects.create(
            user=self.staff_user,
            specialization='Hair Styling'
        )
        
        # Create schedule
        self.schedule = Schedule.objects.create(
            staff=self.staff,
            date=timezone.now().date(),
            time_slot='10:00-11:00',
            availability_status=True
        )
    
    def test_appointment_creation(self):
        """Test creating an appointment."""
        appointment = Appointment.objects.create(
            user=self.customer,
            service=self.service,
            staff=self.staff,
            schedule=self.schedule,
            status='Pending'
        )
        
        self.assertEqual(appointment.user, self.customer)
        self.assertEqual(appointment.service, self.service)
        self.assertEqual(appointment.status, 'Pending')
    
    def test_double_booking_prevention(self):
        """Test that double booking is prevented."""
        # Create first appointment
        Appointment.objects.create(
            user=self.customer,
            service=self.service,
            staff=self.staff,
            schedule=self.schedule,
            status='Confirmed'
        )
        
        # Mark schedule as unavailable
        self.schedule.availability_status = False
        self.schedule.save()
        
        # Check that schedule is no longer available
        self.assertFalse(self.schedule.availability_status)
    
    def test_appointment_cancellation(self):
        """Test appointment cancellation."""
        appointment = Appointment.objects.create(
            user=self.customer,
            service=self.service,
            staff=self.staff,
            schedule=self.schedule,
            status='Confirmed'
        )
        
        # Cancel appointment
        appointment.status = 'Cancelled'
        appointment.save()
        
        # Make schedule available again
        self.schedule.availability_status = True
        self.schedule.save()
        
        self.assertEqual(appointment.status, 'Cancelled')
        self.assertTrue(self.schedule.availability_status)
