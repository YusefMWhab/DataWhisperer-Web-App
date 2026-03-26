from django.contrib import admin
from .models import Project, ProjectFiles
# Register your models here.

class ProjectFilesInline(admin.TabularInline):
    model = ProjectFiles
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_type', 'field_manager', 'is_completed', 'created_at')
    
    inlines = [ProjectFilesInline]
    
    list_filter = ('project_type', 'is_completed', 'field_manager')
    
    search_fields = ('name', 'field_manager__name') 
    
    list_editable = ('is_completed',)