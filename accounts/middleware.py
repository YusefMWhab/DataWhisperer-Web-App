from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse

class GlobalAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            is_allowed = (
                request.path == reverse('auth_page') or 
                request.path.startswith('/admin/') or 
                request.path.startswith('/static/')
            )
            
            if not is_allowed:
                return redirect('auth_page')
        
        else:
            allowed_paths = [reverse('auth_page'), '/admin/']
            if request.path not in allowed_paths and not request.path.startswith('/admin/'):
                if not hasattr(request.user, 'profile') or not request.user.profile.is_allowed_to_login:
                    logout(request)
                    return redirect('auth_page')

        return self.get_response(request)