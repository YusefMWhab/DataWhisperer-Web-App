from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Profile

@receiver(post_save, sender=Profile)
def notify_user_on_activation(sender, instance, created, **kwargs):

    if not created and instance.is_allowed_to_login:
        user_email = instance.user.email
        if user_email: 
            send_mail(
                'DataWhisperer: Account Activated! ✅',
                f'Hi {instance.full_name or instance.user.username},\n\n'
                'Great news! Your account has been approved. You can now login to the dashboard.',
                'noreply@datawhisperer.com',
                [user_email],
                fail_silently=False,
            )