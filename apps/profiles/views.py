from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Profile, UserPhoto, Interest
from .serializers import ProfileSerializer, PhotoSerializer, InterestSerializer

# ==================== TEMPLATE VIEWS ====================

@login_required
def profile_page(request):
    return render(request, 'dashboard/profile.html', {'user': request.user})

@login_required
def edit_profile_page(request):
    return render(request, 'dashboard/edit_profile.html', {'user': request.user})

# ==================== API VIEWS ====================

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

class PhotoUploadView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PhotoSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InterestListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer