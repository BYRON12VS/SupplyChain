from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Profile, Address, UserVerification, UserActivity, UserPreferences


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model
    """
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'email')
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin for Profile model
    """
    list_display = ('user', 'business_name', 'location', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'business_name', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'avatar', 'bio')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Business Information', {
            'fields': ('business_name', 'business_registration_number', 'tax_id', 'website')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Admin for Address model
    """
    list_display = ('user', 'address_type', 'city', 'state', 'country', 'is_default')
    list_filter = ('address_type', 'country', 'is_default')
    search_fields = ('user__username', 'city', 'state', 'country')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    """
    Admin for UserVerification model
    """
    list_display = ('user', 'verification_type', 'status', 'verified_at', 'expires_at')
    list_filter = ('verification_type', 'status', 'created_at')
    search_fields = ('user__username', 'verification_code')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """
    Admin for UserActivity model
    """
    list_display = ('user', 'action_type', 'ip_address', 'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('user__username', 'description', 'ip_address')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """
    Admin for UserPreferences model
    """
    list_display = ('user', 'preferred_language', 'preferred_currency', 'email_notifications', 'sms_notifications')
    list_filter = ('preferred_language', 'preferred_currency', 'email_notifications', 'sms_notifications')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Preferences', {
            'fields': ('email_notifications', 'sms_notifications', 'push_notifications')
        }),
        ('Platform Preferences', {
            'fields': ('preferred_language', 'preferred_currency', 'timezone')
        }),
        ('Marketing Preferences', {
            'fields': ('marketing_emails', 'data_sharing')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
