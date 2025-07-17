import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Profile, UserPreferences, UserVerification, UserActivity


def generate_verification_code(length=6):
    """
    Generate a random verification code
    """
    return ''.join(random.choices(string.digits, k=length))


def create_user_profile(user):
    """
    Create profile and preferences for a new user
    """
    # Create profile
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Create preferences
    preferences, created = UserPreferences.objects.get_or_create(user=user)
    
    return profile, preferences


def log_user_activity(user, action_type, request, description=''):
    """
    Log user activity
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    UserActivity.objects.create(
        user=user,
        action_type=action_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_verification_email(user):
    """
    Send email verification to user
    """
    # Generate verification code
    verification_code = generate_verification_code()
    
    # Create or update verification record
    verification, created = UserVerification.objects.get_or_create(
        user=user,
        verification_type='email',
        defaults={
            'verification_code': verification_code,
            'expires_at': timezone.now() + timedelta(hours=24),
            'status': 'pending'
        }
    )
    
    if not created:
        verification.verification_code = verification_code
        verification.expires_at = timezone.now() + timedelta(hours=24)
        verification.status = 'pending'
        verification.save()
    
    # Send email
    subject = 'Verify Your SupplyChain Account'
    message = f'''
    Dear {user.username},
    
    Please click the link below to verify your email address:
    
    {settings.FRONTEND_URL}/verify-email/{verification_code}
    
    This link will expire in 24 hours.
    
    If you didn't create an account with SupplyChain, please ignore this email.
    
    Best regards,
    SupplyChain Team
    '''
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_password_reset_email(user):
    """
    Send password reset email to user
    """
    # Generate reset token
    reset_token = generate_verification_code(length=32)
    
    # Create or update verification record
    verification, created = UserVerification.objects.get_or_create(
        user=user,
        verification_type='password_reset',
        defaults={
            'verification_code': reset_token,
            'expires_at': timezone.now() + timedelta(hours=1),
            'status': 'pending'
        }
    )
    
    if not created:
        verification.verification_code = reset_token
        verification.expires_at = timezone.now() + timedelta(hours=1)
        verification.status = 'pending'
        verification.save()
    
    # Send email
    subject = 'Reset Your SupplyChain Password'
    message = f'''
    Dear {user.username},
    
    You requested to reset your password. Please click the link below:
    
    {settings.FRONTEND_URL}/reset-password/{reset_token}
    
    This link will expire in 1 hour.
    
    If you didn't request a password reset, please ignore this email.
    
    Best regards,
    SupplyChain Team
    '''
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False


def send_sms_verification(user, phone_number):
    """
    Send SMS verification code to user
    """
    # Generate verification code
    verification_code = generate_verification_code()
    
    # Create or update verification record
    verification, created = UserVerification.objects.get_or_create(
        user=user,
        verification_type='phone',
        defaults={
            'verification_code': verification_code,
            'expires_at': timezone.now() + timedelta(minutes=10),
            'status': 'pending'
        }
    )
    
    if not created:
        verification.verification_code = verification_code
        verification.expires_at = timezone.now() + timedelta(minutes=10)
        verification.status = 'pending'
        verification.save()
    
    # Send SMS (implement with your SMS provider)
    message = f"Your SupplyChain verification code is: {verification_code}"
    
    # This would integrate with SMS service like Twilio, AWS SNS, etc.
    # For now, we'll just print it
    print(f"SMS to {phone_number}: {message}")
    
    return True


def validate_verification_code(user, verification_type, code):
    """
    Validate verification code
    """
    try:
        verification = UserVerification.objects.get(
            user=user,
            verification_type=verification_type,
            verification_code=code,
            status='pending'
        )
        
        if verification.is_expired():
            return False, "Verification code expired"
        
        # Mark as verified
        verification.status = 'verified'
        verification.verified_at = timezone.now()
        verification.save()
        
        return True, "Verification successful"
        
    except UserVerification.DoesNotExist:
        return False, "Invalid verification code"


def get_user_statistics(user):
    """
    Get user statistics for analytics
    """
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    # Get activity count by type
    activity_stats = UserActivity.objects.filter(user=user).values('action_type').annotate(
        count=Count('id')
    )
    
    # Get recent activities (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_activities = UserActivity.objects.filter(
        user=user,
        created_at__gte=thirty_days_ago
    ).count()
    
    return {
        'total_activities': UserActivity.objects.filter(user=user).count(),
        'recent_activities': recent_activities,
        'activity_breakdown': {item['action_type']: item['count'] for item in activity_stats},
        'verification_status': {
            'email': user.is_verified,
            'phone': UserVerification.objects.filter(
                user=user, 
                verification_type='phone', 
                status='verified'
            ).exists()
        }
    }