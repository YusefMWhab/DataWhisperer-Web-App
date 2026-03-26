from django.contrib import admin
from .models import TimeCheckValidationResult

# Register your models here.

@admin.register(TimeCheckValidationResult)
class TimeCheckAdmin(admin.ModelAdmin):
    list_display = ('field_manager_name_snapshot', 'created_at')
    list_filter = ('field_manager', 'created_at')
    search_fields = ('field_manager_name_snapshot', 'project_names')