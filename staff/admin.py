from django.contrib import admin
from .models import FieldManager, ValidationTeamMember

# Register your models here.

@admin.register(FieldManager)
class FieldManagerAdmin(admin.ModelAdmin):
   
    list_display = ('name', 'email', 'has_profile')
    search_fields = ('name', 'email')
    
    
    def has_profile(self, obj):
        return bool(obj.profile)
    has_profile.boolean = True
    has_profile.short_description = 'Linked to Account'


@admin.register(ValidationTeamMember)
class ValidationTeamMemberAdmin(admin.ModelAdmin):
   
    list_display = ('name', 'email', 'has_profile')
    search_fields = ('name', 'email')
    
    
    def has_profile(self, obj):
        return bool(obj.profile)
    has_profile.boolean = True
    has_profile.short_description = 'Linked to Account'