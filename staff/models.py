from django.db import models

# Create your models here.

# Filed Managers Model
class FieldManager(models.Model):
    name = models.CharField(max_length=100, verbose_name="Field Manager Name")
    email = models.EmailField(unique=True, verbose_name="Work Email")

    profile = models.OneToOneField(
        'accounts.UserProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='field_manager_info'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Field Manager"
        verbose_name_plural = "Field Managers"
        ordering = ['name']

#================================================================================================
# Validation Team
class ValidationTeamMember(models.Model):
    name = models.CharField(max_length=100, verbose_name="Full Name")
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="Employee ID")
    email = models.EmailField(unique=True, verbose_name="Work Email")
    
    profile = models.OneToOneField(
        'accounts.UserProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='validation_info'
    )
    
    def __str__(self):
        return f"{self.name} ({self.employee_id})"

    class Meta:
        verbose_name = "Validation Team Member"
        verbose_name_plural = "Validation Team Members"
        ordering = ['name']