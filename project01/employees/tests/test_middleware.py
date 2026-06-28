from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from employees.models import Department, Employee

class MiddlewareTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="IT")
        self.user_with_profile = User.objects.create_user(username="profile_user", password="password")
        self.employee = Employee.objects.create(
            name="Active Employee",
            hire_date=date.today(),
            status="Active",
            position="Dev",
            department=self.dept,
            role="Employee",
            user=self.user_with_profile
        )
        
        self.user_no_profile = User.objects.create_user(username="no_profile_user", password="password")
        
        self.user_inactive_profile = User.objects.create_user(username="inactive_user", password="password")
        self.inactive_employee = Employee.objects.create(
            name="Inactive Employee",
            hire_date=date.today(),
            status="Inactive",
            position="Dev",
            department=self.dept,
            role="Employee",
            user=self.user_inactive_profile
        )

    def test_active_user_with_profile_allowed(self):
        self.client.login(username="profile_user", password="password")
        response = self.client.get('/')
        # Should not redirect to access-denied or login (we expect 200 or 404 depending if dashboard is built)
        self.assertNotEqual(response.status_code, 302)

    def test_user_without_profile_redirected_to_access_denied(self):
        self.client.login(username="no_profile_user", password="password")
        response = self.client.get('/')
        self.assertRedirects(response, '/access-denied/')

    def test_inactive_user_profile_logged_out(self):
        self.client.login(username="inactive_user", password="password")
        response = self.client.get('/')
        # Should redirect to login page because they are logged out
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_get_logout_redirects_to_login(self):
        self.client.login(username="profile_user", password="password")
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
