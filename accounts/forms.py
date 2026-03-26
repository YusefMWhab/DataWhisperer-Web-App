from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import UserProfile

class ExtendedSignupForm(UserCreationForm):
    
    profile_image = forms.ImageField(required=False, label="Profile Picture")
    full_name = forms.CharField(max_length=100, required=True, label="Full Name")
    email = forms.EmailField(required=True, label="Email Address")
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES, 
        required=True, 
        label="Your Role / Position"
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('full_name',)