from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from employees.models import Department, Employee, MenuPermission

class DepartmentCRUDTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept_it = Department.objects.create(name="IT")
        
        # Admin User
        self.admin_user = User.objects.create_user(username="adminuser", password="password")
        self.admin_emp = Employee.objects.create(
            name="Admin User", hire_date=date.today(), status="Active",
            position="HR Manager", department=self.dept_it, role="Admin", user=self.admin_user
        )
        
        # Standard Employee
        self.emp_user = User.objects.create_user(username="empuser", password="password")
        self.emp_emp = Employee.objects.create(
            name="Employee User", hire_date=date.today(), status="Active",
            position="Staff", department=self.dept_it, role="Employee", user=self.emp_user
        )

        # Create default MenuPermissions for testing
        MenuPermission.objects.create(
            menu_name='departments',
            display_name='Department Management',
            allow_superuser=True,
            allow_admin=True,
            allow_manager=False,
            allow_employee=False
        )

    def test_admin_can_access_department_list(self):
        self.client.login(username="adminuser", password="password")
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_access_department_list(self):
        self.client.login(username="empuser", password="password")
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_admin_can_create_department(self):
        self.client.login(username="adminuser", password="password")
        response = self.client.post(reverse('department_create'), {'name': 'Finance'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Department.objects.filter(name="Finance").exists())
