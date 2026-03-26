from django.db import models
from django.core.validators import FileExtensionValidator
import os
# Create your models here.


def project_files_path(instance, filename):
    project_name = instance.project.name.replace(" ", "_")
    return os.path.join('projects', 'documents', project_name, filename)

class Project(models.Model):
    
    PROJECT_TYPE_CHOICES = [
        ('cati', 'CATI'),
        ('field', 'Field'),
        ('mystery', 'Mystery Shopping'),
    ]

    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=255, verbose_name="Project Name")
    
    project_type = models.CharField(
        max_length=20, 
        choices=PROJECT_TYPE_CHOICES, 
        default='field',
        verbose_name="Project Type"
    )
    
    field_manager = models.ForeignKey(
        'staff.FieldManager', 
        on_delete=models.PROTECT,
        null=False,             
        blank=False,              
        related_name='managed_projects',
        verbose_name="Field Manager"
    )
    
    is_completed = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='ongoing',
        verbose_name="Project Status"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")



    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_project_type_display()})"
    
class ProjectFiles(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=project_files_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.project.name} - {self.uploaded_at}"