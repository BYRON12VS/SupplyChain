from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import User, Profile, Address, UserVerification, UserActivity, UserPreferences
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    ProfileSerializer, AddressSerializer, UserVerificationSerializer,
    UserActivitySerializer, UserPreferencesSerializer, PasswordChangeSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer
)
from .utils import create_user_profile, log_user_activity, send_verification_email


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Create user profile and preferences
        create_user_profile(user)
        
        # Log user activity
        log_user_activity(user, 'registration', request)
        
        # Send verification email
        send_verification_email(user)
        
        # Create token for authentication
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Registration successful. Please check your email for verification.'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    API endpoint for user login
    """
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    login(request, user)
    
    # Log user activity
    log_user_activity(user, 'login', request)
    
    # Get or create token
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'user': UserSerializer(user).data,
        'token': token.key,
        'message': 'Login successful'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    API endpoint for user logout
    """
    # Log user activity
    log_user_activity(request.user, 'logout', request)
    
    # Delete token
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
    except Token.DoesNotExist:
        pass
    
    logout(request)
    
    return Response({'message': 'Logout successful'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for detailed profile information
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


class AddressListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating addresses
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for address details
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for user preferences
    """
    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preferences, created = UserPreferences.objects.get_or_create(user=self.request.user)
        return preferences


class UserActivityListView(generics.ListAPIView):
    """
    API endpoint for user activities
    """
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    API endpoint for changing password
    """
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    # Log user activity
    log_user_activity(user, 'password_change', request)
    
    # Delete all tokens to force re-login
    Token.objects.filter(user=user).delete()
    
    return Response({'message': 'Password changed successfully'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    """
    API endpoint for password reset request
    """
    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    user = User.objects.get(email=email)
    
    # Send password reset email (implement this function)
    # send_password_reset_email(user)
    
    return Response({'message': 'Password reset email sent'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    """
    API endpoint for password reset confirmation
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Validate token and reset password (implement token validation)
    # This is a simplified version - you'd need to implement proper token validation
    
    return Response({'message': 'Password reset successful'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_email(request):
    """
    API endpoint for email verification
    """
    user = request.user
    
    # Send verification email
    send_verification_email(user)
    
    return Response({'message': 'Verification email sent'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email_confirm(request, token):
    """
    API endpoint for email verification confirmation
    """
    try:
        verification = UserVerification.objects.get(
            verification_code=token,
            verification_type='email',
            status='pending'
        )
        
        if verification.is_expired():
            return Response({'error': 'Verification token expired'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        user = verification.user
        user.is_verified = True
        user.save()
        
        verification.status = 'verified'
        verification.save()
        
        return Response({'message': 'Email verified successfully'})
        
    except UserVerification.DoesNotExist:
        return Response({'error': 'Invalid verification token'}, 
                       status=status.HTTP_400_BAD_REQUEST)