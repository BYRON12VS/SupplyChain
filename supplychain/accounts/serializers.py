from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Profile, Address, UserVerification, UserActivity, UserPreferences


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'user_type', 'phone_number')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('Account is deactivated')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must provide username and password')
        
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for user addresses
    """
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class UserVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for user verification
    """
    class Meta:
        model = UserVerification
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for user activities
    """
    class Meta:
        model = UserActivity
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


class UserPreferencesSerializer(serializers.ModelSerializer):
    """
    Serializer for user preferences
    """
    class Meta:
        model = UserPreferences
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details
    """
    profile = ProfileSerializer(read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    preferences = UserPreferencesSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'phone_number', 
                 'is_verified', 'is_active', 'date_joined', 'profile', 
                 'addresses', 'preferences')
        read_only_fields = ('id', 'date_joined', 'is_verified')


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset request
    """
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    """
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs