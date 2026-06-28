import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project01.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Department, Employee, MenuPermission

# Create admin user
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
    print("Created superuser admin/admin12345")
else:
    u = User.objects.get(username='admin')
    # Reset password to admin12345 to ensure consistency
    u.set_password('admin12345')
    u.save()
    print("User admin already exists, password set to admin12345")

# Create departments
it, _ = Department.objects.get_or_create(name='IT')
hr, _ = Department.objects.get_or_create(name='HR')
fin, _ = Department.objects.get_or_create(name='Finance')
print("Departments seeded: IT, HR, Finance")

# Create employee profile
if not Employee.objects.filter(user=u).exists():
    Employee.objects.create(
        name='System Administrator',
        hire_date=datetime.date.today(),
        status='Active',
        position='Super Admin',
        department=it,
        role='Super User',
        user=u
    )
    print("Seeded Employee profile for admin")
else:
    print("Employee profile for admin already exists")

# Seed Menu Permissions
MenuPermission.objects.get_or_create(
    menu_name='employees',
    defaults={'display_name': 'Employee Directory', 'allow_superuser': True, 'allow_admin': True}
)
MenuPermission.objects.get_or_create(
    menu_name='departments',
    defaults={'display_name': 'Department Management', 'allow_superuser': True, 'allow_admin': True}
)
print("Menu permissions seeded")

