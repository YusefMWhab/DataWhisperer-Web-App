from django.contrib import admin
from .models import itime

# Register your models here.

@admin.register(itime)
class itimeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'display_projects', 'is_exported')
    
    list_filter = ('date', 'employee', 'is_exported')
    
    search_fields = ('employee__name',)

    date_hierarchy = 'date'
    
    list_editable = ('date', 'is_exported',)

    def display_projects(self, obj):
        return ", ".join([p.name for p in obj.projects.all()])
    
    display_projects.short_description = 'Projects Worked On'

    ordering = ('-date',)
