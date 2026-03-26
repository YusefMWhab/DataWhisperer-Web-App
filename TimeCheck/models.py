from django.db import models
from django.conf import settings
from staff.models import FieldManager
# Create your models here.


# Time Check Validation Rresults Model
class TimeCheckValidationResult(models.Model):

    # 1. Field Manager Name (ForeignKey)
    field_manager = models.ForeignKey(
        FieldManager, 
        on_delete=models.SET_NULL,
        null=True,              
        blank=True,             
        related_name='validation_results',
        verbose_name="Field Manager"
    )

    # 2. User
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL, 
    on_delete=models.SET_NULL,
    null=True, 
    blank=True,
    related_name = 'time_check_validations',
    verbose_name = "Processed By (User)"
) 
    # 3. Snapshot for field
    field_manager_name_snapshot = models.CharField(max_length=150, verbose_name="Field Manager Name at Upload")

    # 4. Project Names
    project_names = models.JSONField(default=list, verbose_name="Project Names (Scripts)")

    # 5. Validation Date
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Validation Date")

    # 6. Validation Reports
    overlap_report = models.TextField(null=True, blank=True, verbose_name="Time Overlaps")
    daily_count_report = models.TextField(null=True, blank=True, verbose_name="Daily Interview Count") 
    out_working_hours_report = models.TextField(null=True, blank=True, verbose_name="Outside Working Hours")
    loi_report = models.TextField(null=True, blank=True, verbose_name="Length of Interview (LOI)")

    # 7. Row Data
    raw_data = models.TextField(null=True, blank=True, verbose_name="Original Data")

    def __str__(self):
        date_str = self.created_at.strftime('%Y-%m-%d %H:%M')
        return f"Result for {self.field_manager_name_snapshot} - {date_str}"

    class Meta:
        verbose_name = "Time Check Validation Result"
        verbose_name_plural = "Time Check Validation Results"
        ordering = ['-created_at']