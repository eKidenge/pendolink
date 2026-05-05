from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import TemplateView

def home_redirect(request):
    # Always show public dashboard for non-authenticated users
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin-dashboard')
        return redirect('dashboard')
    # Show public dashboard for users not logged in
    return redirect('public-dashboard')

urlpatterns = [
    path('', home_redirect, name='home'),
    path('public/', TemplateView.as_view(template_name='dashboard/public_dashboard.html'), name='public-dashboard'),
    path('admin/', admin.site.urls),
    path('admin-panel/', include('apps.admin_panel.urls')),
    path('auth/', include('apps.users.urls')),
    path('', include('apps.matching.urls')),
    path('', include('apps.chat.urls')),
    path('profiles/', include('apps.profiles.urls')),
    path('locations/', include('apps.locations.urls')),
    path('ai/', include('apps.ai_engine.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('billing/', include('apps.billing.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('moderation/', include('apps.moderation.urls')),
    
    # API URLs
    path('api/auth/', include('apps.users.urls')),
    path('api/profiles/', include('apps.profiles.urls')),
    path('api/locations/', include('apps.locations.urls')),
    path('api/matching/', include('apps.matching.urls')),
    path('api/ai/', include('apps.ai_engine.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/billing/', include('apps.billing.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/moderation/', include('apps.moderation.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)