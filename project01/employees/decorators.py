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
