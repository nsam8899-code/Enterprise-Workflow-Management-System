from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from employees.models import Department, Employee

class EmployeeCRUDTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept_it = Department.objects.create(name="IT")
        self.dept_hr = Department.objects.create(name="HR")
        
        # Admin User
        self.admin_user = User.objects.create_user(username="adminuser", password="password")
        self.admin_emp = Employee.objects.create(
            name="Admin User", hire_date=date.today(), status="Active",
            position="Director", department=self.dept_it, role="Admin", user=self.admin_user
        )
        
        # Standard Employee 1
        self.user1 = User.objects.create_user(username="staff1", password="password")
        self.emp1 = Employee.objects.create(
            name="Alice Developer", hire_date=date.today(), status="Active",
            position="Staff", department=self.dept_it, role="Employee", user=self.user1
        )

        # Standard Employee 2
        self.user2 = User.objects.create_user(username="staff2", password="password")
        self.emp2 = Employee.objects.create(
            name="Bob Recruiter", hire_date=date.today(), status="Active",
            position="Recruiter", department=self.dept_hr, role="Employee", user=self.user2
        )

    def test_admin_can_access_employee_list(self):
        self.client.login(username="adminuser", password="password")
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Developer")
        self.assertContains(response, "Bob Recruiter")

    def test_employee_search(self):
        self.client.login(username="adminuser", password="password")
        response = self.client.get(reverse('employee_list') + '?search=Alice')
        self.assertContains(response, "Alice Developer")
        self.assertNotContains(response, "Bob Recruiter")

    def test_employee_filter_by_dept(self):
        self.client.login(username="adminuser", password="password")
        response = self.client.get(reverse('employee_list') + f'?department={self.dept_hr.id}')
        self.assertContains(response, "Bob Recruiter")
        self.assertNotContains(response, "Alice Developer")
