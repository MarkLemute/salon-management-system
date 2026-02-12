from django.test import TestCase
from django.contrib.auth import get_user_model
from backend.accounts.models import User


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='Customer'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'Customer')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_authentication(self):
        """Test user login."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        from django.contrib.auth import authenticate
        authenticated_user = authenticate(username='testuser', password='testpass123')
        
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.username, 'testuser')
    
    def test_user_roles(self):
        """Test different user roles."""
        admin = User.objects.create_user(username='admin', password='pass', role='Admin')
        staff = User.objects.create_user(username='staff', password='pass', role='Staff')
        customer = User.objects.create_user(username='customer', password='pass', role='Customer')
        
        self.assertEqual(admin.role, 'Admin')
        self.assertEqual(staff.role, 'Staff')
        self.assertEqual(customer.role, 'Customer')
