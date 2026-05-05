from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, SendMessageSerializer
from apps.notifications.services import NotificationService

# ==================== TEMPLATE VIEW ====================

@login_required
def chat_template(request):
    """Render the chat HTML template"""
    return render(request, 'dashboard/chat.html', {
        'user': request.user
    })

# ==================== API VIEWS ====================

class ConversationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(
            Q(match__user1=self.request.user) | Q(match__user2=self.request.user),
            is_active=True
        ).order_by('-updated_at')

class ConversationDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(
            Q(match__user1=self.request.user) | Q(match__user2=self.request.user)
        )

class MessageListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        conversation = Conversation.objects.get(id=conversation_id)
        
        # Verify user is part of conversation
        if conversation.match.user1 != self.request.user and conversation.match.user2 != self.request.user:
            return Message.objects.none()
        
        # Mark messages as read
        unread_messages = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=self.request.user)
        unread_messages.update(is_read=True, read_at=models.DateTimeField(auto_now=True))
        
        return Message.objects.filter(conversation=conversation)

class SendMessageView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SendMessageSerializer
    
    def perform_create(self, serializer):
        conversation_id = self.kwargs['conversation_id']
        conversation = Conversation.objects.get(id=conversation_id)
        
        message = serializer.save(
            conversation=conversation,
            sender=self.request.user
        )
        
        # Send notification to recipient
        recipient = conversation.match.user2 if conversation.match.user1 == self.request.user else conversation.match.user1
        NotificationService.send_message_notification(recipient, conversation, message)
        
        # Update conversation timestamp
        conversation.save()

class DeleteMessageView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, message_id):
        try:
            message = Message.objects.get(id=message_id, sender=request.user)
            message.delete()
            return Response({'status': 'deleted'}, status=status.HTTP_200_OK)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)