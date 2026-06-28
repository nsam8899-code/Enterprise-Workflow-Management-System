from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import models
from django.core.paginator import Paginator
from employees.decorators import menu_permission_required
from employees.models import Department, Employee
from employees.forms import DepartmentForm, EmployeeForm

def access_denied(request):
    return render(request, 'employees/access_denied.html')

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    employee = getattr(request, 'employee', None)
    return render(request, 'employees/dashboard.html', {'employee': employee})

@login_required
@menu_permission_required('departments')
def department_list(request):
    departments = Department.objects.all().order_by('name')
    return render(request, 'employees/department_list.html', {'departments': departments})

@login_required
@menu_permission_required('departments')
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
@menu_permission_required('departments')
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
@menu_permission_required('departments')
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        return redirect('department_list')
    return render(request, 'employees/department_confirm_delete.html', {'department': department})

@login_required
@menu_permission_required('employees')
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
    desc_mode = request.GET.get('desc', 'false')
    if sort_by in ['employee_id', 'name', 'department__name', 'hire_date']:
        sort_field = f"-{sort_by}" if desc_mode == 'true' else sort_by
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
        'desc_mode': desc_mode,
    })

@login_required
@menu_permission_required('employees')
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
@menu_permission_required('employees')
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
@menu_permission_required('employees')
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})
