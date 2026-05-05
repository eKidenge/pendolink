from django.urls import path
from .views import (
    RegisterView, LoginView, UserProfileView,
    login_page, register_page, logout_view, CustomLoginView, register_submit
)

urlpatterns = [
    # Template pages (for browser)
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', register_page, name='register'),
    path('register/submit/', register_submit, name='register_submit'),
    path('logout/', logout_view, name='logout'),
    
    # API endpoints (for mobile app/Postman)
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/profile/', UserProfileView.as_view(), name='api_profile'),
]