from django.contrib.auth.forms import AuthenticationForm
from .forms import ExtendedSignupForm
from django.contrib.auth import login as auth_login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache

@never_cache
def auth_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    login_form = AuthenticationForm()
    signup_form = ExtendedSignupForm()
    active_tab = 'login' 

    if request.method == 'POST':
        if 'signup_submit' in request.POST:
            active_tab = 'signup'
            signup_form = ExtendedSignupForm(request.POST, request.FILES) 
            
            if signup_form.is_valid():
                user = signup_form.save(commit=False)
                
                full_name = signup_form.cleaned_data.get('full_name', '')
                email_address = signup_form.cleaned_data.get('email')
                name_parts = full_name.split(' ', 1)
                
                user.first_name = name_parts[0]
                user.email = email_address
                user.last_name = name_parts[1] if len(name_parts) > 1 else ''
                user.save() 
                
                
                profile = user.profile
                profile.full_name = full_name
                profile.email = email_address
                profile.role = signup_form.cleaned_data.get('role')
                if 'profile_image' in request.FILES:
                    profile.image = request.FILES['profile_image']

                profile.save()

                # If Userprofile related to any table in staff
                # 1. Field managers
                from staff.models import FieldManager
                if profile.role == 'field_manager':
                    FieldManager = FieldManager.objects.filter(email=email_address).first()
                    if FieldManager:
                        FieldManager.profile = profile
                        FieldManager.save()
                        profile.save()

                # 2. Validation Team
                from staff.models import ValidationTeamMember
                if profile.role == 'validator':
                    ValidationTeamMember = ValidationTeamMember.objects.filter(email=email_address).first()
                    if ValidationTeamMember:
                        ValidationTeamMember.profile = profile
                        ValidationTeamMember.save()
                        profile.save()

                messages.success(request, "Account has been created successfully. Wait for activation")
                return redirect('auth_page')
            else:
                
                messages.error(request, "Error.")
        
        elif 'login_submit' in request.POST:
            active_tab = 'login'
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                if hasattr(user, 'profile') and user.profile.is_allowed_to_login:
                    auth_login(request, user)
                    return redirect('dashboard')
                else:
                    messages.warning(request, "Your account is pendding for activation")
            else:
                messages.error(request, "Username or Password is not correct")

    context = {
        'login_form': login_form,
        'signup_form': signup_form,
        'active_tab': active_tab,
    }
    return render(request, 'auth.html', context)

def logout_view(request):
    logout(request)
    return redirect('auth_page')