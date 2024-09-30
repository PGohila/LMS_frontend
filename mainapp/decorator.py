from functools import wraps
from django.shortcuts import redirect, render

# def custom_login_required(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         # Check if the session variable exists
#         if 'so_token' not in request.session or 'user_token' not in request.session:
#             return redirect('login')
#         return view_func(request, *args, **kwargs)
#     return _wrapped_view

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the session variable exists
        if  'user_token' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def custom_permission(*permission_value):
    print('permission_value',permission_value)
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if the session variable exists        
            permission_list=request.session['permission'] 
            print('anyyyyy',any(permission in permission_list for permission in permission_value))
            if not any(permission in permission_list for permission in permission_value):
                return render(request, "page_not_found.html")
            return view_func(request, *args, **kwargs)           
        return _wrapped_view
    return decorator
