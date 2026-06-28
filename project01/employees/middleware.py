from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout

class EmployeeProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.allowed_menus = []
        exempt_urls = [
            reverse('login'),
            '/access-denied/',
        ]
        
        try:
            exempt_urls.append(reverse('logout'))
        except Exception:
            pass

        # Skip verification for exempt URLs and static files
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
                
                # Fetch allowed menu list dynamically
                role = employee.role
                from employees.models import MenuPermission
                request.allowed_menus = [
                    p.menu_name for p in MenuPermission.objects.all() if p.is_allowed(role)
                ]
            except AttributeError:
                # No employee profile found for user
                return redirect('/access-denied/')
                
        return self.get_response(request)
