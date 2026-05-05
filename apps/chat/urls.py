from django.urls import path
from .views import (
    ConversationListView, ConversationDetailView,
    MessageListView, SendMessageView, DeleteMessageView,
    chat_template
)

urlpatterns = [
    # Template page
    path('', chat_template, name='chat'),
    
    # API endpoints
    path('api/conversations/', ConversationListView.as_view(), name='conversations'),
    path('api/conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('api/conversations/<int:conversation_id>/messages/', MessageListView.as_view(), name='messages'),
    path('api/conversations/<int:conversation_id>/send/', SendMessageView.as_view(), name='send-message'),
    path('api/messages/<int:message_id>/delete/', DeleteMessageView.as_view(), name='delete-message'),
]