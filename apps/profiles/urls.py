from django.urls import path
from django.views.generic import RedirectView
from .views import ProfileView, PhotoUploadView, InterestListView, profile_page, edit_profile_page

urlpatterns = [
    # Template pages
    path('my/', profile_page, name='profile'),  # ADD THIS - gives you 'profile' URL name
    path('edit/', edit_profile_page, name='edit-profile'),
    
    # API endpoints
    path('api/my-profile/', ProfileView.as_view(), name='api_profile'),
    path('api/upload-photo/', PhotoUploadView.as_view(), name='api_upload_photo'),
    path('api/interests/', InterestListView.as_view(), name='api_interests'),
]