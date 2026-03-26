from django.db import models
from django.utils import timezone

# Create your models here.
class itime(models.Model):
    employee = models.ForeignKey(
        'staff.ValidationTeamMember', 
        on_delete=models.CASCADE,
        related_name='daily_logs',
        verbose_name="Employee"
    )
    date = models.DateField(default=timezone.now, verbose_name="Date")
    
    projects = models.ManyToManyField(
        'projects.Project', 
        blank=True, 
        related_name='daily_attendances'
    )

    is_exported = models.BooleanField(
        default=False, 
        verbose_name="Exported to Payroll",
    )

    
    class Meta:
        unique_together = ('employee', 'date')
        verbose_name = "iTime Record"
        verbose_name_plural = "iTime Records"

    def __str__(self):
        return f"{self.employee.name} - {self.date}"