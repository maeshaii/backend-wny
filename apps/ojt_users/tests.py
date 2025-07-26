from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User as AuthUser
from apps.shared.models import User
from .models import OjtUser
from datetime import date

# Create your tests here.

class OjtUserModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            user_id=1,
            acc_username='test123',
            f_name='John',
            l_name='Doe',
            course='Computer Science',
            year_graduated=2023,
            user_status='Active',
            gender='Male',
            email='john.doe@example.com'
        )
        
        # Create a test OJT user
        self.ojt_user = OjtUser.objects.create(
            user=self.user,
            ojt_status='approved',
            company_name='Tech Corp',
            position_title='Software Developer Intern',
            department='IT',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            total_hours=480,
            supervisor_name='Jane Smith',
            supervisor_contact='+1234567890',
            supervisor_email='jane.smith@techcorp.com',
            stipend_amount=5000.00,
            requirements_submitted=True,
            evaluation_score=4.5
        )
    
    def test_ojt_user_creation(self):
        """Test that OJT user can be created successfully"""
        self.assertEqual(self.ojt_user.user.f_name, 'John')
        self.assertEqual(self.ojt_user.company_name, 'Tech Corp')
        self.assertEqual(self.ojt_user.ojt_status, 'approved')
    
    def test_ojt_user_str_representation(self):
        """Test the string representation of OJT user"""
        expected = f"OJT Profile - {self.user.f_name} {self.user.l_name}"
        self.assertEqual(str(self.ojt_user), expected)
    
    def test_ojt_user_properties(self):
        """Test OJT user properties"""
        self.assertEqual(self.ojt_user.full_name, 'John Doe')
        self.assertTrue(self.ojt_user.is_active_ojt)
        self.assertEqual(self.ojt_user.duration_days, 181)  # 6 months approximately
    
    def test_ojt_user_status_choices(self):
        """Test OJT status choices"""
        status_choices = [choice[0] for choice in OjtUser.OJT_STATUS_CHOICES]
        self.assertIn('pending', status_choices)
        self.assertIn('approved', status_choices)
        self.assertIn('rejected', status_choices)
        self.assertIn('completed', status_choices)
        self.assertIn('ongoing', status_choices)

class OjtUserViewsTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            user_id=1,
            acc_username='test123',
            f_name='John',
            l_name='Doe',
            course='Computer Science',
            year_graduated=2023,
            user_status='Active',
            gender='Male',
            email='john.doe@example.com'
        )
        
        # Create a test OJT user
        self.ojt_user = OjtUser.objects.create(
            user=self.user,
            ojt_status='approved',
            company_name='Tech Corp',
            position_title='Software Developer Intern'
        )
    
    def test_ojt_users_list_view(self):
        """Test the OJT users list view"""
        response = self.client.get('/api/ojt-users/list/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['ojt_users']), 1)
        self.assertEqual(data['ojt_users'][0]['company_name'], 'Tech Corp')
    
    def test_ojt_user_detail_view(self):
        """Test the OJT user detail view"""
        response = self.client.get(f'/api/ojt-users/{self.ojt_user.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['ojt_user']['company_name'], 'Tech Corp')
    
    def test_ojt_user_by_user_id_view(self):
        """Test getting OJT user by user ID"""
        response = self.client.get(f'/api/ojt-users/user/{self.user.user_id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['ojt_user']['user_id'], self.user.user_id)
