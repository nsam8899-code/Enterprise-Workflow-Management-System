from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from employees.models import Department, Employee

class ModelTestCase(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="IT")
        self.user1 = User.objects.create_user(username="testuser1", password="password")
        self.user2 = User.objects.create_user(username="testuser2", password="password")

    def test_create_department(self):
        self.assertEqual(self.dept.name, "IT")

    def test_employee_id_auto_generation(self):
        emp1 = Employee.objects.create(
            name="Somchai Dee",
            hire_date=date.today(),
            status="Active",
            position="Developer",
            department=self.dept,
            role="Employee",
            user=self.user1
        )
        self.assertEqual(emp1.employee_id, "EMP0001")

        emp2 = Employee.objects.create(
            name="Somsri Rak",
            hire_date=date.today(),
            status="Active",
            position="Manager",
            department=self.dept,
            role="Manager",
            user=self.user2
        )
        self.assertEqual(emp2.employee_id, "EMP0002")
