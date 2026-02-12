from django.test import TestCase
from backend.services.models import Service


class ServiceTest(TestCase):
    """Test cases for Service model."""
    
    def test_service_creation(self):
        """Test creating a service."""
        service = Service.objects.create(
            name='Haircut',
            description='Professional haircut service',
            price=25.00,
            duration=30
        )
        
        self.assertEqual(service.name, 'Haircut')
        self.assertEqual(float(service.price), 25.00)
        self.assertEqual(service.duration, 30)
        self.assertTrue(service.is_active)
    
    def test_service_string_representation(self):
        """Test service string representation."""
        service = Service.objects.create(
            name='Manicure',
            price=20.00,
            duration=45
        )
        
        self.assertEqual(str(service), 'Manicure - $20.00')
    
    def test_service_list(self):
        """Test listing active services."""
        Service.objects.create(name='Service 1', price=10, duration=30, is_active=True)
        Service.objects.create(name='Service 2', price=20, duration=60, is_active=True)
        Service.objects.create(name='Service 3', price=30, duration=90, is_active=False)
        
        active_services = Service.objects.filter(is_active=True)
        
        self.assertEqual(active_services.count(), 2)
