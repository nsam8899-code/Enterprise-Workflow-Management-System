# Enterprise Workflow Management System (Phase 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a robust Django-based Enterprise Workflow Management System (Phase 1) featuring user authentication, custom middleware verification, role-based authorization, dynamic department administration, and a searchable employee directory styled with a collapsible sidebar and theme toggle.

**Architecture:** A monolithic Django application utilizing a OneToOne relation between the standard `User` and a custom `Employee` model. Authentication is validated through a custom middleware, and access control is enforced at the view layer using decorators. The frontend uses server-rendered Django Templates styled with Vanilla CSS and interactive Vanilla JS for client-side state (theme preference, sidebar collapse state).

**Tech Stack:** Django 6.0.2, SQLite, HTML5, JavaScript (ES6+), Vanilla CSS (responsive grid, CSS custom properties).

## Global Constraints
* Database: Standard SQLite database (`project01/db.sqlite3`).
* Styling: Vanilla CSS (no external styling frameworks like TailwindCSS).
* Interactivity: Vanilla JavaScript only (no external frameworks for dynamic elements).
* Authentication: Username and Password login; unlinked Django users are redirected to access denied page.
* Theme support: Light Mode (Enterprise Indigo) and Dark Mode (Slate Tech), switchable via button, persistent in `localStorage`.
* Sidebar: Collapsible navigation bar.

---

### Task 1: Django App Setup & Data Models

**Files:**
* Create: `project01/employees/__init__.py`
* Create: `project01/employees/models.py`
* Create: `project01/employees/tests/__init__.py`
* Create: `project01/employees/tests/test_models.py`
* Modify: `project01/project01/settings.py`

**Interfaces:**
* Produces: `Department` model with `name` CharField.
* Produces: `Employee` model with `employee_id`, `name`, `hire_date`, `status`, `position`, `department`, `role`, and `user` OneToOneField.
* Produces: Auto-generating sequential Employee ID logic (`EMP0001`, `EMP0002` etc.) in `Employee.save()`.

- [ ] **Step 1: Create the app folder structure and register the app**
  Create the folder `project01/employees` and empty files `__init__.py`, `models.py`. Register the app in `project01/project01/settings.py` by adding `'employees',` to `INSTALLED_APPS`.
  
- [ ] **Step 2: Write failing unit tests for Employee and Department models**
  Create `project01/employees/tests/__init__.py` and `project01/employees/tests/test_models.py` with tests for model creation and auto-generation of Employee ID.
  
  ```python
  # project01/employees/tests/test_models.py
  from django.test import TestCase
  from django.contrib.auth.models import User
  from django.core.exceptions import ValidationError
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
  ```

- [ ] **Step 3: Run the test to verify it fails**
  Run: `python project01/manage.py test employees.tests.test_models`
  Expected: FAIL (ImportError or AttributeError because models do not exist)

- [ ] **Step 4: Implement Department and Employee models**
  Write models inside `project01/employees/models.py`.
  
  ```python
  # project01/employees/models.py
  from django.db import db, models
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
  ```

- [ ] **Step 5: Generate and run migrations**
  Run: `python project01/manage.py makemigrations employees`
  Run: `python project01/manage.py migrate`
  Expected: Successful migrations execution.

- [ ] **Step 6: Run tests to verify they pass**
  Run: `python project01/manage.py test employees.tests.test_models`
  Expected: PASS

- [ ] **Step 7: Commit**
  Run: `git add project01/employees/models.py project01/employees/tests/test_models.py project01/project01/settings.py`
  Run: `git commit -m "feat: setup employees app and define Department and Employee models"`

---

### Task 2: Authentication & Profile Verification Middleware

**Files:**
* Create: `project01/employees/middleware.py`
* Create: `project01/employees/tests/test_middleware.py`
* Modify: `project01/project01/settings.py`
* Create: `project01/employees/views.py` (access denied view)
* Create: `project01/employees/templates/employees/access_denied.html`

**Interfaces:**
* Produces: `EmployeeProfileMiddleware` that blocks active users without an employee profile, or inactive/resigned profiles.
* Produces: `/access-denied/` view and page.
* Produces: Custom decorators `@superuser_or_admin_required`.

- [ ] **Step 1: Write failing tests for Middleware authentication & verification rules**
  Create `project01/employees/tests/test_middleware.py` containing:
  
  ```python
  # project01/employees/tests/test_middleware.py
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
  ```

- [ ] **Step 2: Run the test to verify it fails**
  Run: `python project01/manage.py test employees.tests.test_middleware`
  Expected: FAIL

- [ ] **Step 3: Implement access denied view and registration**
  Create a basic view in `project01/employees/views.py` and map it in URL routing.
  Create template `project01/employees/templates/employees/access_denied.html`.
  
  ```python
  # project01/employees/views.py (add placeholder first)
  from django.shortcuts import render, redirect
  from django.contrib.auth import logout
  
  def access_denied(self):
      # We will return the view. We can write a custom function view.
      pass
  ```

- [ ] **Step 4: Implement the Middleware**
  Create `project01/employees/middleware.py` and register it in `MIDDLEWARE` list in `project01/project01/settings.py` (after `AuthenticationMiddleware`).
  
  ```python
  # project01/employees/middleware.py
  from django.shortcuts import redirect
  from django.urls import reverse
  from django.contrib.auth import logout

  class EmployeeProfileMiddleware:
      def __init__(self, get_response):
          self.get_response = get_response

      def __call__(self, request):
          # Skip verification for login, logout, static files, and access-denied view itself
          exempt_urls = [
              reverse('login'),
              reverse('logout') if 'logout' in request.resolver_match.view_name else None,
              '/access-denied/',
          ]
          
          # Check URL path
          if request.path in exempt_urls or request.path.startswith('/static/'):
              return self.get_response(request)

          if request.user.is_authenticated:
              try:
                  employee = request.user.employee
                  if employee.status in ['Inactive', 'Resigned']:
                      logout(request)
                      return redirect('login')
                  # Attach employee profile to request object
                  request.employee = employee
              except AttributeError:
                  # No employee profile found for user
                  if request.path != '/access-denied/':
                      return redirect('/access-denied/')
                      
          return self.get_response(request)
  ```

- [ ] **Step 5: Write Custom decorators**
  In `project01/employees/decorators.py`, write role-based checkers:
  
  ```python
  # project01/employees/decorators.py
  from django.core.exceptions import PermissionDenied
  from django.shortcuts import redirect

  def superuser_or_admin_required(view_func):
      def _wrapped_view_func(request, *args, **kwargs):
          if not request.user.is_authenticated:
              return redirect('login')
          if hasattr(request, 'employee') and request.employee.role in ['Super User', 'Admin']:
              return view_func(request, *args, **kwargs)
          raise PermissionDenied
      return _wrapped_view_func
  ```

- [ ] **Step 6: Run tests to verify they pass**
  Run: `python project01/manage.py test employees.tests.test_middleware`
  Expected: PASS

- [ ] **Step 7: Commit**
  Run: `git add project01/employees/middleware.py project01/employees/decorators.py project01/employees/tests/test_middleware.py`
  Run: `git commit -m "feat: add EmployeeProfileMiddleware and superuser_or_admin_required decorator"`

---

### Task 3: Department Management CRUD

**Files:**
* Modify: `project01/employees/views.py`
* Create: `project01/employees/forms.py`
* Create: `project01/employees/templates/employees/department_list.html`
* Create: `project01/employees/templates/employees/department_form.html`
* Create: `project01/employees/templates/employees/department_confirm_delete.html`
* Create: `project01/employees/urls.py`
* Modify: `project01/project01/urls.py`
* Create: `project01/employees/tests/test_departments.py`

**Interfaces:**
* Produces: `DepartmentForm` validator.
* Produces: `/departments/` routing with views `department_list`, `department_create`, `department_edit`, `department_delete`.
* Consumes: `Department` database model.

- [ ] **Step 1: Write failing tests for Department CRUD authorization & actions**
  Create `project01/employees/tests/test_departments.py`:
  
  ```python
  # project01/employees/tests/test_departments.py
  from django.test import TestCase, Client
  from django.contrib.auth.models import User
  from django.urls import reverse
  from datetime import date
  from employees.models import Department, Employee

  class DepartmentCRUDTestCase(TestCase):
      def setUp(self):
          self.client = Client()
          self.dept_it = Department.objects.create(name="IT")
          
          # Admin
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
  ```

- [ ] **Step 2: Run the test to verify it fails**
  Run: `python project01/manage.py test employees.tests.test_departments`
  Expected: FAIL

- [ ] **Step 3: Implement DepartmentForm**
  Create `project01/employees/forms.py`:
  
  ```python
  # project01/employees/forms.py
  from django import forms
  from employees.models import Department

  class DepartmentForm(forms.ModelForm):
      class Meta:
          model = Department
          fields = ['name']
          widgets = {
              'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter department name'}),
          }
  ```

- [ ] **Step 4: Implement CRUD views**
  Inside `project01/employees/views.py`, write view classes/functions. We will use standard Class-Based Views (CBVs) or function views with decorators.
  Let's use function views with the decorator `@superuser_or_admin_required`.
  
  ```python
  # project01/employees/views.py (additions)
  from django.shortcuts import render, redirect, get_object_or_001_project, get_object_or_404
  from django.contrib.auth.decorators import login_required
  from employees.decorators import superuser_or_admin_required
  from employees.models import Department
  from employees.forms import DepartmentForm

  @login_required
  @superuser_or_admin_required
  def department_list(request):
      departments = Department.objects.all().order_by('name')
      return render(request, 'employees/department_list.html', {'departments': departments})

  @login_required
  @superuser_or_admin_required
  def department_create(request):
      if request.method == 'POST':
          form = DepartmentForm(request.POST)
          if form.is_valid():
              form.save()
              return redirect('department_list')
      else:
          form = DepartmentForm()
      return render(request, 'employees/department_form.html', {'form': form, 'title': 'Create Department'})

  @login_required
  @superuser_or_admin_required
  def department_edit(request, pk):
      department = get_object_or_404(Department, pk=pk)
      if request.method == 'POST':
          form = DepartmentForm(request.POST, instance=department)
          if form.is_valid():
              form.save()
              return redirect('department_list')
      else:
          form = DepartmentForm(instance=department)
      return render(request, 'employees/department_form.html', {'form': form, 'title': 'Edit Department'})

  @login_required
  @superuser_or_admin_required
  def department_delete(request, pk):
      department = get_object_or_404(Department, pk=pk)
      if request.method == 'POST':
          department.delete()
          return redirect('department_list')
      return render(request, 'employees/department_confirm_delete.html', {'department': department})
  ```

- [ ] **Step 5: Setup URL mappings**
  Create `project01/employees/urls.py` and wire it to `project01/project01/urls.py`.
  
  ```python
  # project01/employees/urls.py
  from django.urls import path
  from employees import views

  urlpatterns = [
      path('departments/', views.department_list, name='department_list'),
      path('departments/create/', views.department_create, name='department_create'),
      path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
      path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
  ]
  ```
  
  Modify `project01/project01/urls.py` to include `employees.urls`.

- [ ] **Step 6: Write simple templates**
  Create minimal HTML files inside `project01/employees/templates/employees/` to render forms and tables (styling will be layered in Task 5).

- [ ] **Step 7: Run tests to verify they pass**
  Run: `python project01/manage.py test employees.tests.test_departments`
  Expected: PASS

- [ ] **Step 8: Commit**
  Run: `git add project01/employees/views.py project01/employees/forms.py project01/employees/urls.py project01/project01/urls.py project01/employees/tests/test_departments.py`
  Run: `git commit -m "feat: implement department list, create, edit, and delete features with role checks"`

---

### Task 4: Employee Directory CRUD & Search Engine

**Files:**
* Modify: `project01/employees/views.py`
* Modify: `project01/employees/forms.py`
* Create: `project01/employees/templates/employees/employee_list.html`
* Create: `project01/employees/templates/employees/employee_form.html`
* Create: `project01/employees/templates/employees/employee_confirm_delete.html`
* Create: `project01/employees/tests/test_employees.py`

**Interfaces:**
* Consumes: `Employee` model.
* Produces: `EmployeeForm` (with user login mapping field filtered to unused Django User records).
* Produces: `/employees/` with sorting, filtering, searching and pagination views.

- [ ] **Step 1: Write failing tests for Employee CRUD, sorting, and filters**
  Create `project01/employees/tests/test_employees.py`:
  
  ```python
  # project01/employees/tests/test_employees.py
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
  ```

- [ ] **Step 2: Run the test to verify it fails**
  Run: `python project01/manage.py test employees.tests.test_employees`
  Expected: FAIL

- [ ] **Step 3: Implement EmployeeForm**
  Modify `project01/employees/forms.py` to add `EmployeeForm`. Ensure the `user` field query filters out users who are already linked to an Employee profile, but includes the user currently linked when editing.
  
  ```python
  # project01/employees/forms.py (additions)
  from django.contrib.auth.models import User
  from employees.models import Employee

  class EmployeeForm(forms.ModelForm):
      class Meta:
          model = Employee
          fields = ['name', 'hire_date', 'status', 'position', 'department', 'role', 'user']
          widgets = {
              'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
              'name': forms.TextInput(attrs={'class': 'form-control'}),
              'status': forms.Select(attrs={'class': 'form-control'}),
              'position': forms.TextInput(attrs={'class': 'form-control'}),
              'department': forms.Select(attrs={'class': 'form-control'}),
              'role': forms.Select(attrs={'class': 'form-control'}),
              'user': forms.Select(attrs={'class': 'form-control'}),
          }

      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          # Filter standard Users who don't have an Employee associated yet
          linked_user_ids = Employee.objects.exclude(user__isnull=True).values_list('user_id', flat=True)
          
          # If we are editing, we should include the currently linked user
          if self.instance and self.instance.user_id:
              # Exclude the current instance's user_id from the list of excluded ids
              linked_user_ids = [uid for uid in linked_user_ids if uid != self.instance.user_id]

          self.fields['user'].queryset = User.objects.exclude(id__in=linked_user_ids)
          self.fields['user'].required = True
  ```

- [ ] **Step 4: Implement Employee directory views (including search/sort/filter/paginate)**
  Add Employee views in `project01/employees/views.py`:
  
  ```python
  # project01/employees/views.py (additions)
  from django.core.paginator import Paginator
  from employees.decorators import superuser_or_admin_required

  @login_required
  @superuser_or_admin_required
  def employee_list(request):
      queryset = Employee.objects.all().select_related('department', 'user')
      
      # Search
      search_query = request.GET.get('search', '')
      if search_query:
          queryset = queryset.filter(
              models.Q(name__icontains=search_query) | 
              models.Q(employee_id__icontains=search_query)
          )
          
      # Filters
      dept_filter = request.GET.get('department', '')
      if dept_filter:
          queryset = queryset.filter(department_id=dept_filter)
          
      status_filter = request.GET.get('status', '')
      if status_filter:
          queryset = queryset.filter(status=status_filter)
          
      position_filter = request.GET.get('position', '')
      if position_filter:
          queryset = queryset.filter(position__icontains=position_filter)
          
      # Sorting
      sort_by = request.GET.get('sort', 'employee_id')
      if sort_by in ['employee_id', 'name', 'department__name', 'hire_date']:
          desc = request.GET.get('desc', 'false') == 'true'
          sort_field = f"-{sort_by}" if desc else sort_by
          queryset = queryset.order_by(sort_field)
      else:
          queryset = queryset.order_by('employee_id')

      # Pagination
      paginator = Paginator(queryset, 10)
      page_number = request.GET.get('page')
      page_obj = paginator.get_page(page_number)

      departments = Department.objects.all()
      
      return render(request, 'employees/employee_list.html', {
          'page_obj': page_obj,
          'departments': departments,
          'search_query': search_query,
          'dept_filter': dept_filter,
          'status_filter': status_filter,
          'position_filter': position_filter,
          'sort_by': sort_by,
          'desc_mode': request.GET.get('desc', 'false'),
      })

  @login_required
  @superuser_or_admin_required
  def employee_create(request):
      if request.method == 'POST':
          form = EmployeeForm(request.POST)
          if form.is_valid():
              form.save()
              return redirect('employee_list')
      else:
          form = EmployeeForm()
      return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Create Employee'})

  @login_required
  @superuser_or_admin_required
  def employee_edit(request, pk):
      employee = get_object_or_404(Employee, pk=pk)
      if request.method == 'POST':
          form = EmployeeForm(request.POST, instance=employee)
          if form.is_valid():
              form.save()
              return redirect('employee_list')
      else:
          form = EmployeeForm(instance=employee)
      return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Edit Employee'})

  @login_required
  @superuser_or_admin_required
  def employee_delete(request, pk):
      employee = get_object_or_404(Employee, pk=pk)
      if request.method == 'POST':
          employee.delete()
          return redirect('employee_list')
      return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})
  ```

- [ ] **Step 5: Register URLs**
  Update `project01/employees/urls.py`:
  
  ```python
  # project01/employees/urls.py (additions)
  path('employees/', views.employee_list, name='employee_list'),
  path('employees/create/', views.employee_create, name='employee_create'),
  path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
  path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
  path('access-denied/', views.access_denied, name='access_denied'),
  path('', views.dashboard, name='dashboard'), # Dashboard/Home
  ```

- [ ] **Step 6: Run tests to verify they pass**
  Run: `python project01/manage.py test employees.tests.test_employees`
  Expected: PASS

- [ ] **Step 7: Commit**
  Run: `git add project01/employees/views.py project01/employees/forms.py project01/employees/urls.py project01/employees/tests/test_employees.py`
  Run: `git commit -m "feat: add employee directory views, forms, search, sort, filter, and pagination"`

---

### Task 5: CSS Design System, Templates, Theme, and Sidebar Switchers

**Files:**
* Create: `project01/employees/static/employees/css/style.css`
* Create: `project01/employees/static/employees/js/main.js`
* Create: `project01/employees/templates/employees/base.html`
* Create: `project01/employees/templates/employees/dashboard.html`
* Create: `project01/employees/templates/employees/login.html`
* Create: `project01/employees/templates/employees/access_denied.html`
* Modify: `project01/employees/templates/employees/employee_list.html`
* Modify: `project01/employees/templates/employees/employee_form.html`
* Modify: `project01/employees/templates/employees/department_list.html`
* Modify: `project01/employees/templates/employees/department_form.html`

**Interfaces:**
* Produces: A premium styling system supporting dynamic Light Mode (Indigo) and Dark Mode (Slate Tech).
* Produces: Interactive sidebar toggle controls (desktop collapsed layout, mobile drawer layout).
* Produces: Premium aesthetic pages for Login, Dashboard, Directories, and CRUD.

- [ ] **Step 1: Write static script with theme initialization and sidebar toggle handler**
  Create `project01/employees/static/employees/js/main.js`:
  
  ```javascript
  // project01/employees/static/employees/js/main.js
  
  // Theme Switching
  function initTheme() {
      const savedTheme = localStorage.getItem('theme') || 'light';
      if (savedTheme === 'dark') {
          document.body.classList.add('dark-mode');
      } else {
          document.body.classList.remove('dark-mode');
      }
  }

  function toggleTheme() {
      if (document.body.classList.contains('dark-mode')) {
          document.body.classList.remove('dark-mode');
          localStorage.setItem('theme', 'light');
      } else {
          document.body.classList.add('dark-mode');
          localStorage.setItem('theme', 'dark');
      }
  }

  // Sidebar toggling
  function toggleSidebar() {
      const container = document.querySelector('.app-container');
      if (container) {
          container.classList.toggle('sidebar-collapsed');
      }
  }

  document.addEventListener('DOMContentLoaded', () => {
      initTheme();
      
      const themeToggleBtn = document.getElementById('theme-toggle');
      if (themeToggleBtn) {
          themeToggleBtn.addEventListener('click', toggleTheme);
      }
      
      const sidebarToggleBtn = document.getElementById('sidebar-toggle');
      if (sidebarToggleBtn) {
          sidebarToggleBtn.addEventListener('click', toggleSidebar);
      }
  });
  ```

- [ ] **Step 2: Create Custom CSS styling system with theme support**
  Create `project01/employees/static/employees/css/style.css`:
  Define variables under `:root` for Enterprise Indigo Light and `body.dark-mode` for Slate Tech Dark Mode. Style standard components: table, form, sidebar, header, alert cards, buttons. Ensure layout classes (`.app-container`, `.sidebar`, `.main-content`, `.header`, `.footer`) are fully supported and transitions are smooth.

- [ ] **Step 3: Define Base Template (`base.html`)**
  Create `project01/employees/templates/employees/base.html`:
  Include a blocking script in the `<head>` to initialize theme immediately and prevent white flash. Construct layout containing a collapsible sidebar with links (Dashboard, Employee Directory, Departments) and a top header containing the sidebar toggle, theme toggle, and logged-in user credentials.

- [ ] **Step 4: Style Login and Dashboard Templates**
  Create `project01/employees/templates/employees/login.html` and `dashboard.html`. Add widgets to standard views (e.g. login form, dashboard status metrics, current profile card).

- [ ] **Step 5: Style Employee and Department templates**
  Update list tables and form templates in `project01/employees/templates/employees/` with CSS classes defined in `style.css` (e.g., table styling, hover indicators, sort direction tags, responsive form inputs).

- [ ] **Step 6: Run server and perform manual verification**
  Run: `python project01/manage.py runserver`
  Verify the layout, theme toggle button, and sidebar collapse button dynamically in the browser.

- [ ] **Step 7: Commit**
  Run: `git add project01/employees/static/ project01/employees/templates/`
  Run: `git commit -m "style: implement global styles, base layout, light/dark theme, and collapsible sidebar"`
