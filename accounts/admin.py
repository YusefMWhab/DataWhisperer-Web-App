from django.utils.html import format_html
from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        'show_photo',
        'user', 'get_email', 
        'full_name',
        'role',
        'is_allowed_to_login', 
        'can_access_time_check_tool',
        'can_access_iTime_tool',
        'can_export_iTime_sheet',
        'can_mark_iTime_as_exported',
        'can_access_Projects_tool')
    
    list_editable = (
        'is_allowed_to_login', 
        'can_access_time_check_tool', 
        'can_access_iTime_tool',
        'can_export_iTime_sheet',
        'can_mark_iTime_as_exported',
        'can_access_Projects_tool')
    
    search_fields = (
        'full_name', 
        'email', 
        'user__username')
    
    list_filter = (
        'role',
        'is_allowed_to_login', 
        'can_access_time_check_tool', 
        'can_access_iTime_tool',
        'can_export_iTime_sheet',
        'can_mark_iTime_as_exported',
        'can_access_Projects_tool')
    

    def show_photo(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 50%;" />', obj.image.url)
        return "No Photo"

    show_photo.short_description = 'Photo'

    def get_email(self, obj):
        return obj.email
    get_email.short_description = 'Email Address'