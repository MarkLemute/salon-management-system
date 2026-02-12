from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def role_required(*roles):
    """
    Decorator to check if user has required role.
    Usage: @role_required('Admin', 'Staff')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('login')
            
            if request.user.role not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                # Redirect based on role
                if request.user.role == 'Admin':
                    return redirect('admin_dashboard')
                elif request.user.role == 'Staff':
                    return redirect('staff_dashboard')
                else:
                    return redirect('customer_dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator to restrict access to Admin users only."""
    return role_required('Admin')(view_func)


def staff_or_admin_required(view_func):
    """Decorator to restrict access to Staff or Admin users."""
    return role_required('Admin', 'Staff')(view_func)


def customer_only(view_func):
    """Decorator to restrict access to Customer users only."""
    return role_required('Customer')(view_func)
