from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from django.contrib import messages
from .models import User
from apps.profiles.models import Profile, Interest
from apps.locations.models import Location
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

# ==================== TEMPLATE VIEWS (for browser) ====================

def login_page(request):
    """Render login page"""
    return render(request, 'auth/login.html')

def register_page(request):
    """Render register page"""
    interests = Interest.objects.all()
    return render(request, 'auth/register.html', {'interests': interests})

def logout_view(request):
    """Logout user and redirect to login page"""
    auth_logout(request)
    return redirect('login')

def register_submit(request):
    """Handle form submission for registration"""
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        looking_for = request.POST.get('looking_for')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        bio = request.POST.get('bio')
        occupation = request.POST.get('occupation')
        education = request.POST.get('education')
        city = request.POST.get('city')
        town = request.POST.get('town')
        interests = request.POST.getlist('interests')
        
        # Validation dictionary
        errors = {}
        
        # Validate required fields
        if not username:
            errors['username'] = 'Username is required'
        if not email:
            errors['email'] = 'Email is required'
        if not phone_number:
            errors['phone_number'] = 'Phone number is required'
        if not date_of_birth:
            errors['date_of_birth'] = 'Date of birth is required'
        if not password:
            errors['password'] = 'Password is required'
        if not city:
            errors['city'] = 'City is required'
        if not town:
            errors['town'] = 'Town is required'
        
        # Validate passwords match
        if password and password2 and password != password2:
            errors['password'] = 'Passwords do not match'
        
        # Validate username uniqueness
        if username and User.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists'
        
        # Validate email uniqueness
        if email and User.objects.filter(email=email).exists():
            errors['email'] = 'Email already exists'
        
        # Validate phone uniqueness
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            errors['phone_number'] = 'Phone number already registered'
        
        # If errors, return to register page with errors
        if errors:
            return render(request, 'auth/register.html', {
                'errors': errors,
                'form_data': request.POST,
                'interests': Interest.objects.all()
            })
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            phone_number=phone_number,
            password=password,
            date_of_birth=date_of_birth,
            gender=gender,
            looking_for=looking_for
        )
        
        # Create or get profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.bio = bio or ''
        profile.occupation = occupation or ''
        profile.education = education or ''
        profile.interests = interests
        profile.save()
        
        # Create location
        Location.objects.create(
            user=user,
            city=city,
            town=town
        )
        
        # Log the user in
        auth_login(request, user)
        
        # Add success message
        messages.success(request, f'Welcome to PendoLink, {username}!')
        
        # Redirect based on role
        if user.is_staff or user.is_superuser:
            return redirect('admin-dashboard')
        return redirect('dashboard')
    
    # If not POST, redirect to register page
    return redirect('register')

class CustomLoginView(AuthLoginView):
    """Custom login view with template - Role based redirect"""
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect based on user role"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return reverse('admin-dashboard')
        else:
            return reverse('dashboard')
    
    def form_invalid(self, form):
        """Handle invalid login"""
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)

# ==================== API VIEWS (for mobile/Postman) ====================

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user