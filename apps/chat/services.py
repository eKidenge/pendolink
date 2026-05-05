from .models import Conversation, Message
from apps.notifications.services import NotificationService

class ChatService:
    def __init__(self, user):
        self.user = user
    
    def send_message(self, conversation_id, content):
        """Send a message in a conversation"""
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            
            # Verify user is in conversation
            if conversation.match.user1 != self.user and conversation.match.user2 != self.user:
                return {'success': False, 'error': 'Unauthorized'}
            
            # Check if chat is active
            if not conversation.is_active:
                return {'success': False, 'error': 'Conversation is inactive'}
            
            # Create message
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content
            )
            
            # Update conversation timestamp
            conversation.save()
            
            # Send notification to recipient
            recipient = conversation.match.user2 if conversation.match.user1 == self.user else conversation.match.user1
            NotificationService.send_message_notification(recipient, conversation, message)
            
            return {'success': True, 'message_id': message.id}
            
        except Conversation.DoesNotExist:
            return {'success': False, 'error': 'Conversation not found'}
    
    def mark_messages_read(self, conversation_id):
        """Mark all messages in conversation as read"""
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            
            Message.objects.filter(
                conversation=conversation,
                is_read=False
            ).exclude(sender=self.user).update(is_read=True)
            
            return {'success': True}
            
        except Conversation.DoesNotExist:
            return {'success': False}
    
    def get_unread_count(self):
        """Get total unread messages for user"""
        conversations = Conversation.objects.filter(
            Q(match__user1=self.user) | Q(match__user2=self.user),
            is_active=True
        )
        
        total = 0
        for conv in conversations:
            total += conv.messages.filter(is_read=False).exclude(sender=self.user).count()
        
        return total