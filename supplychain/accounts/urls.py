from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile URLs
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/details/', views.ProfileDetailView.as_view(), name='profile-details'),
    path('preferences/', views.UserPreferencesView.as_view(), name='preferences'),
    
    # Address URLs
    path('addresses/', views.AddressListCreateView.as_view(), name='addresses'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
    
    # Activity URLs
    path('activities/', views.UserActivityListView.as_view(), name='activities'),
    
    # Password management URLs
    path('change-password/', views.change_password, name='change-password'),
    path('password-reset/', views.password_reset_request, name='password-reset'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password-reset-confirm'),
    
    # Verification URLs
    path('verify-email/', views.verify_email, name='verify-email'),
    path('verify-email/<str:token>/', views.verify_email_confirm, name='verify-email-confirm'),
]