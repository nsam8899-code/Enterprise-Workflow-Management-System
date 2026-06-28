from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Resigned', 'Resigned'),
    ]
    ROLE_CHOICES = [
        ('Super User', 'Super User'),
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    ]

    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=150)
    hire_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    position = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.employee_id:
            # Get the highest sequential employee_id
            last_emp = Employee.objects.filter(employee_id__startswith='EMP').order_by('-employee_id').first()
            if last_emp:
                try:
                    last_num = int(last_emp.employee_id[3:])
                    new_num = last_num + 1
                except ValueError:
                    new_num = 1
            else:
                new_num = 1
            self.employee_id = f"EMP{new_num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_id} - {self.name}"


class MenuPermission(models.Model):
    menu_name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    allow_superuser = models.BooleanField(default=True)
    allow_admin = models.BooleanField(default=True)
    allow_manager = models.BooleanField(default=False)
    allow_employee = models.BooleanField(default=False)

    def is_allowed(self, role):
        if role == 'Super User':
            return self.allow_superuser
        elif role == 'Admin':
            return self.allow_admin
        elif role == 'Manager':
            return self.allow_manager
        elif role == 'Employee':
            return self.allow_employee
        return False

    def __str__(self):
        return self.display_name
