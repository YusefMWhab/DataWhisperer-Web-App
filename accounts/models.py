from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

# For save img path
class UserProfile(models.Model):
    

    ROLE_CHOICES = [
        ('field_manager', 'Field Manager'),
        ('validator', 'Validation Team'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    full_name = models.CharField(max_length=255, null=True, blank=True)

    email = models.EmailField(max_length=255, null=True, blank=True)
    
    image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # 1. Allow Login
    is_allowed_to_login = models.BooleanField(default=False)
    # 2. Allow Access Timecheck Tool
    can_access_time_check_tool = models.BooleanField(default=False)
    # 3. Allow Access ITime Tool
    can_access_iTime_tool = models.BooleanField(default=False)
    # 4. Allow Export ITime sheet
    can_export_iTime_sheet = models.BooleanField(default=False)
    # 5. Allow Mark ITime as Exported
    can_mark_iTime_as_exported = models.BooleanField(default=False)
    # 6. Allow Access ITime Tool
    can_access_Projects_tool = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.full_name or ''}"
    
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()