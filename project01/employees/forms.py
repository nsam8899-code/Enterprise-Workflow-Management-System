from django import forms
from django.contrib.auth.models import User
from employees.models import Department, Employee

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter department name'}),
        }

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
            linked_user_ids = [uid for uid in linked_user_ids if uid != self.instance.user_id]

        self.fields['user'].queryset = User.objects.exclude(id__in=linked_user_ids)
        self.fields['user'].required = True


from django.forms import modelformset_factory
from employees.models import MenuPermission

MenuPermissionFormSet = modelformset_factory(
    MenuPermission,
    fields=('allow_admin', 'allow_manager', 'allow_employee'),
    extra=0
)

