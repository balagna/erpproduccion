from functools import wraps
from flask import abort
from flask_login import current_user

def permission_required(permission_name):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
            if not current_user.has_permission(permission_name):
                return abort(403)
            return view(*args, **kwargs)
        return wrapper
    return decorator

def superadmin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(401)
        if not current_user.is_superadmin():
            return abort(403)
        return view(*args, **kwargs)
    return wrapper
