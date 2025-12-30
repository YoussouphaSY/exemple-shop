from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()


def role_required(allowed_roles):
    """Decorator to restrict access based on user role."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, "Vous n'avez pas les permissions nécessaires.")
                return HttpResponseForbidden("Accès refusé")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Decorator for admin-only views."""
    return role_required(['admin', 'Administrateur'])(view_func)


def manager_or_admin_cashier_required(view_func):
    """Decorator for manager and admin views."""
    return role_required(['admin', 'manager', 'cashier', 'Administrateur', 'Gestionnaire', 'Caissier'])(view_func)


def cashier_access(view_func):
    """Decorator for cashier access (sales only)."""
    return role_required(['admin', 'manager', 'cashier', 'Administrateur', 'Gestionnaire', 'Caissier'])(view_func)