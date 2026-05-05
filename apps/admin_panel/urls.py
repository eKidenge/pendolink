from django.urls import path
from .views import admin_dashboard, admin_users, admin_reports, admin_analytics

urlpatterns = [
    path('', admin_dashboard, name='admin-dashboard'),
    path('users/', admin_users, name='admin-users'),
    path('reports/', admin_reports, name='admin-reports'),
    path('analytics/', admin_analytics, name='admin-analytics'),
]