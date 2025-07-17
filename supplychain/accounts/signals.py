from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import User, Profile, UserPreferences, Address
from .utils import log_user_activity, create_user_profile


@receiver(post_save, sender=User)
def create_user_profile_and_preferences(sender, instance, created, **kwargs):
    """
    Create profile and preferences when a new user is created
    """
    if created:
        create_user_profile(instance)


@receiver(pre_save, sender=Address)
def ensure_single_default_address(sender, instance, **kwargs):
    """
    Ensure only one default address per user per address type
    """
    if instance.is_default:
        # Set all other addresses of the same type to non-default
        Address.objects.filter(
            user=instance.user,
            address_type=instance.address_type,
            is_default=True
        ).exclude(pk=instance.pk).update(is_default=False)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log user login activity
    """
    log_user_activity(user, 'login', request)


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log user logout activity
    """
    if user:
        log_user_activity(user, 'logout', request)