from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from employees.decorators import superuser_or_admin_required
from employees.models import Department
from employees.forms import DepartmentForm

def access_denied(request):
    return render(request, 'employees/access_denied.html')

def dashboard(request):
    # Temporary placeholder for tests, will be replaced with real dashboard later
    return HttpResponse("Welcome to dashboard")

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
