from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from employees.models import Department, Employee, MenuPermission

class PermissionViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="IT")
        self.perm = MenuPermission.objects.create(
            menu_name='employees',
            display_name="Emp",
            allow_superuser=True,
            allow_admin=False,
            allow_manager=False,
            allow_employee=False
        )
        
        # Super User
        self.su_user = User.objects.create_user(username="superuser", password="password")
        self.su_emp = Employee.objects.create(
            name="SU User", hire_date=date.today(), status="Active",
            position="Sysop", department=self.dept, role="Super User", user=self.su_user
        )
        # Admin
        self.admin_user = User.objects.create_user(username="adminuser", password="password")
        self.admin_emp = Employee.objects.create(
            name="Admin User", hire_date=date.today(), status="Active",
            position="Admin", department=self.dept, role="Admin", user=self.admin_user
        )

    def test_superuser_can_access_permission_page(self):
        self.client.login(username="superuser", password="password")
        response = self.client.get(reverse('menu_permissions_edit'))
        self.assertEqual(response.status_code, 200)

    def test_admin_cannot_access_permission_page(self):
        self.client.login(username="adminuser", password="password")
        response = self.client.get(reverse('menu_permissions_edit'))
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_save_menu_permissions(self):
        self.client.login(username="superuser", password="password")
        # Get request first to ensure the page has a valid formset format
        response = self.client.get(reverse('menu_permissions_edit'))
        self.assertEqual(response.status_code, 200)
        
        # Post request to modify permissions
        # formset fields prefix: form-
        post_data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-id': str(self.perm.id),
            'form-0-allow_admin': 'on', # Check admin
            'form-0-allow_manager': '', # Uncheck manager
            'form-0-allow_employee': '', # Uncheck employee
        }
        
        response = self.client.post(reverse('menu_permissions_edit'), post_data)
        self.assertRedirects(response, reverse('dashboard'))
        
        # Verify the database updated
        self.perm.refresh_from_db()
        self.assertTrue(self.perm.allow_superuser) # remains True (or read-only / default)
        self.assertTrue(self.perm.allow_admin)
        self.assertFalse(self.perm.allow_manager)
        self.assertFalse(self.perm.allow_employee)
