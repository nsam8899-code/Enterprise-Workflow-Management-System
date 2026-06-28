# Dynamic Menu Permissions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a dynamic menu permissions administration matrix for Super Users, allowing them to configure which employee roles can view and access the sidebar navigation items.

**Architecture:** A database-backed permission system using a custom `MenuPermission` model. The middleware queries this configuration dynamically on every request to compute allowed paths, replacing hardcoded role checks in views and templates.

**Tech Stack:** Django 6.0.2, SQLite, HTML5, CSS3, JS.

## Global Constraints
* No external frameworks. Vanilla CSS and JS.
* Only Super Users can access the configuration view.
* Database seeding must ensure default visibility configurations exist on startup.

---

### Task 1: `MenuPermission` Model & Seeding

**Files:**
* Modify: `project01/employees/models.py`
* Create: `project01/employees/tests/test_permissions.py`
* Modify: `project01/seed.py`

**Interfaces:**
* Produces: `MenuPermission` model with helper `is_allowed(self, role)`.

- [ ] **Step 1: Write failing tests for MenuPermission model**
  Create `project01/employees/tests/test_permissions.py`:
  
  ```python
  from django.test import TestCase
  from employees.models import MenuPermission

  class MenuPermissionModelTestCase(TestCase):
      def test_menu_permission_allowed_roles(self):
          perm = MenuPermission.objects.create(
              menu_name="employees",
              display_name="Employee Directory",
              allow_superuser=True,
              allow_admin=True,
              allow_manager=False,
              allow_employee=False
          )
          self.assertTrue(perm.is_allowed("Super User"))
          self.assertTrue(perm.is_allowed("Admin"))
          self.assertFalse(perm.is_allowed("Manager"))
          self.assertFalse(perm.is_allowed("Employee"))
  ```

- [ ] **Step 2: Run the test to verify it fails**
  Run: `python project01/manage.py test employees.tests.test_permissions`
  Expected: FAIL

- [ ] **Step 3: Implement MenuPermission Model**
  Open `project01/employees/models.py` and append `MenuPermission`:
  
  ```python
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
  ```

- [ ] **Step 4: Create and run migrations**
  Run: `python project01/manage.py makemigrations employees`
  Run: `python project01/manage.py migrate`
  Expected: Success

- [ ] **Step 5: Update seed.py**
  Add logic to `project01/seed.py` to seed default permissions:
  
  ```python
  # Add to project01/seed.py
  MenuPermission.objects.get_or_create(
      menu_name='employees',
      defaults={'display_name': 'Employee Directory', 'allow_superuser': True, 'allow_admin': True}
  )
  MenuPermission.objects.get_or_create(
      menu_name='departments',
      defaults={'display_name': 'Department Management', 'allow_superuser': True, 'allow_admin': True}
  )
  print("Menu permissions seeded")
  ```

- [ ] **Step 6: Run seed script and verify tests pass**
  Run: `python project01/seed.py`
  Run: `python project01/manage.py test employees.tests.test_permissions`
  Expected: PASS

- [ ] **Step 7: Commit**
  Run: `git add project01/employees/models.py project01/employees/tests/test_permissions.py project01/seed.py`
  Run: `git commit -m "feat: add MenuPermission model and seed default records"`

---

### Task 2: Dynamic Middleware & Routing Integration

**Files:**
* Modify: `project01/employees/middleware.py`
* Modify: `project01/employees/decorators.py`
* Modify: `project01/employees/templates/employees/base.html`
* Modify: `project01/employees/tests/test_middleware.py`

**Interfaces:**
* Consumes: `MenuPermission` model.
* Produces: `request.allowed_menus` containing list of allowed menu names for the current user's role.

- [ ] **Step 1: Write failing middleware permission tests**
  Add tests inside `project01/employees/tests/test_middleware.py` asserting that when we change `MenuPermission` values, middleware blocks or permits user access accordingly:
  
  ```python
  def test_dynamic_permission_enforcement(self):
      # Initially Employee cannot access departments
      self.client.login(username="empuser", password="password")
      response = self.client.get(reverse('department_list'))
      self.assertEqual(response.status_code, 403)

      # Update permission to allow Employees
      perm = MenuPermission.objects.get(menu_name='departments')
      perm.allow_employee = True
      perm.save()

      response = self.client.get(reverse('department_list'))
      self.assertEqual(response.status_code, 200) # Now allowed
  ```

- [ ] **Step 2: Run tests to verify failure**
  Run: `python project01/manage.py test employees.tests.test_middleware`
  Expected: FAIL

- [ ] **Step 3: Update EmployeeProfileMiddleware**
  Open `project01/employees/middleware.py` and query permissions dynamically:
  
  ```python
  # inside EmployeeProfileMiddleware.__call__
  if request.user.is_authenticated:
      try:
          employee = request.user.employee
          if employee.status in ['Inactive', 'Resigned']:
              logout(request)
              return redirect('login')
          request.employee = employee
          
          # Fetch allowed menu list dynamically
          role = employee.role
          from employees.models import MenuPermission
          request.allowed_menus = [
              p.menu_name for p in MenuPermission.objects.all() if p.is_allowed(role)
          ]
      except AttributeError:
          return redirect('/access-denied/')
  ```

- [ ] **Step 4: Update custom decorators**
  Modify `project01/employees/decorators.py` to use dynamic permissions.
  Instead of static role checks, we will create a dynamic decorator `@menu_permission_required(menu_name)`:
  
  ```python
  from django.core.exceptions import PermissionDenied
  from django.shortcuts import redirect

  def menu_permission_required(menu_name):
      def decorator(view_func):
          def _wrapped_view_func(request, *args, **kwargs):
              if not request.user.is_authenticated:
                  return redirect('login')
              if hasattr(request, 'allowed_menus') and menu_name in request.allowed_menus:
                  return view_func(request, *args, **kwargs)
              raise PermissionDenied
          return _wrapped_view_func
      return decorator
  ```
  
  Update imports and decorator calls in `project01/employees/views.py`:
  - Replace `@superuser_or_admin_required` with `@menu_permission_required('employees')` on employee views.
  - Replace `@superuser_or_admin_required` with `@menu_permission_required('departments')` on department views.

- [ ] **Step 5: Update Sidebar Layout (`base.html`)**
  Replace role checks with `request.allowed_menus` checks:
  
  ```html
  <!-- project01/employees/templates/employees/base.html -->
  {% if 'employees' in request.allowed_menus %}
  <li class="{% if 'employee' in request.resolver_match.view_name %}active{% endif %}">
      <a href="{% url 'employee_list' %}">
          <span class="icon">👥</span>
          <span class="label-text">Employees</span>
      </a>
  </li>
  {% endif %}
  {% if 'departments' in request.allowed_menus %}
  <li class="{% if 'department' in request.resolver_match.view_name %}active{% endif %}">
      <a href="{% url 'department_list' %}">
          <span class="icon">🏢</span>
          <span class="label-text">Departments</span>
      </a>
  </li>
  {% endif %}
  ```

- [ ] **Step 6: Run tests to verify they pass**
  Run: `python project01/manage.py test`
  Expected: PASS

- [ ] **Step 7: Commit**
  Run: `git add project01/employees/middleware.py project01/employees/decorators.py project01/employees/views.py project01/employees/templates/employees/base.html project01/employees/tests/`
  Run: `git commit -m "feat: implement dynamic menu permissions in middleware, views, and templates"`

---

### Task 3: Super User Configuration Form & View

**Files:**
* Modify: `project01/employees/views.py`
* Modify: `project01/employees/forms.py`
* Modify: `project01/employees/urls.py`
* Create: `project01/employees/templates/employees/menu_permissions_form.html`
* Modify: `project01/employees/templates/employees/dashboard.html`
* Create: `project01/employees/tests/test_permission_views.py`

**Interfaces:**
* Produces: `/menu-permissions/` URL view, accessible only to Super User.
* Produces: Form edit visibility matrix saving to database.

- [ ] **Step 1: Write failing tests for permission configuration views**
  Create `project01/employees/tests/test_permission_views.py`:
  
  ```python
  from django.test import TestCase, Client
  from django.contrib.auth.models import User
  from django.urls import reverse
  from datetime import date
  from employees.models import Department, Employee, MenuPermission

  class PermissionViewsTestCase(TestCase):
      def setUp(self):
          self.client = Client()
          self.dept = Department.objects.create(name="IT")
          MenuPermission.objects.create(menu_name='employees', display_name="Emp")
          
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
  ```

- [ ] **Step 2: Run tests to verify failure**
  Run: `python project01/manage.py test employees.tests.test_permission_views`
  Expected: FAIL

- [ ] **Step 3: Create MenuPermission Form**
  Open `project01/employees/forms.py` and add:
  
  ```python
  from django.forms import modelformset_factory
  from employees.models import MenuPermission

  MenuPermissionFormSet = modelformset_factory(
      MenuPermission,
      fields=('allow_admin', 'allow_manager', 'allow_employee'),
      extra=0
  )
  ```

- [ ] **Step 4: Implement view and URL**
  Modify `project01/employees/views.py` to add:
  
  ```python
  from django.core.exceptions import PermissionDenied
  from employees.forms import MenuPermissionFormSet

  @login_required
  def menu_permissions_edit(request):
      # Strictly check Super User role
      if not hasattr(request, 'employee') or request.employee.role != 'Super User':
          raise PermissionDenied
          
      if request.method == 'POST':
          formset = MenuPermissionFormSet(request.POST)
          if formset.is_valid():
              formset.save()
              return redirect('dashboard')
      else:
          formset = MenuPermissionFormSet()
          
      return render(request, 'employees/menu_permissions_form.html', {'formset': formset})
  ```
  
  Register URL pattern in `project01/employees/urls.py`:
  `path('menu-permissions/', views.menu_permissions_edit, name='menu_permissions_edit'),`

- [ ] **Step 5: Create template and Dashboard button**
  Create `project01/employees/templates/employees/menu_permissions_form.html` styled with the Indigo theme. It renders the formset in a grid layout table.
  Update `project01/employees/templates/employees/dashboard.html` to add button:
  
  ```html
  {% if employee.role == 'Super User' %}
      <a href="{% url 'menu_permissions_edit' %}" class="btn btn-primary" style="justify-content: center; background-color: #6366f1; border-color: #4f46e5;">Manage Menu Permissions</a>
  {% endif %}
  ```

- [ ] **Step 6: Run tests to verify they pass**
  Run: `python project01/manage.py test`
  Expected: PASS

- [ ] **Step 7: Commit**
  Run: `git add project01/employees/views.py project01/employees/forms.py project01/employees/urls.py project01/employees/templates/ project01/employees/tests/`
  Run: `git commit -m "feat: add menu permission edit view and template for Super User"`
