from django.urls import path
from .views import (
    NotificationListView, MarkNotificationReadView, MarkAllReadView,
    NotificationPreferencesView, UnreadCountView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications'),
    path('<int:notification_id>/read/', MarkNotificationReadView.as_view(), name='mark-read'),
    path('mark-all-read/', MarkAllReadView.as_view(), name='mark-all-read'),
    path('preferences/', NotificationPreferencesView.as_view(), name='preferences'),
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),
]