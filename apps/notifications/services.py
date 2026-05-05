from .models import Notification

class NotificationService:
    
    @staticmethod
    def send_notification(user, notification_type, title, message, data=None):
        """Send a notification to a user"""
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data or {}
        )
        
        # TODO: Send push notification via Firebase/FCM
        # TODO: Send email notification if enabled
        
        return notification
    
    @staticmethod
    def send_match_notification(user, match):
        """Send match notification"""
        return NotificationService.send_notification(
            user=user,
            notification_type='match',
            title='New Match! 🎉',
            message=f"You matched with {match.get_other_user(user).username}! Start chatting now.",
            data={'match_id': match.id, 'action_url': f'/chat/{match.conversation.id}/'}
        )
    
    @staticmethod
    def send_like_notification(user, liked_by):
        """Send like notification"""
        return NotificationService.send_notification(
            user=user,
            notification_type='like',
            title='Someone liked you! 💕',
            message=f"{liked_by.username} liked your profile. Like them back to match!",
            data={'liked_by_id': liked_by.id, 'action_url': '/discover/'}
        )
    
    @staticmethod
    def send_message_notification(user, conversation, message):
        """Send message notification"""
        other_user = conversation.match.user2 if conversation.match.user1 == message.sender else conversation.match.user1
        
        return NotificationService.send_notification(
            user=user,
            notification_type='message',
            title=f'New message from {other_user.username}',
            message=message.content[:100],
            data={'conversation_id': conversation.id, 'action_url': f'/chat/{conversation.id}/'}
        )
    
    @staticmethod
    def send_premium_notification(user, plan_name):
        """Send premium subscription notification"""
        return NotificationService.send_notification(
            user=user,
            notification_type='premium',
            title='Welcome to Premium! ✨',
            message=f"You're now on the {plan_name} plan. Enjoy unlimited matches!",
            data={'action_url': '/dashboard/'}
        )
    
    @staticmethod
    def send_boost_notification(user, duration):
        """Send profile boost notification"""
        return NotificationService.send_notification(
            user=user,
            notification_type='boost',
            title='Your profile is boosted! 🚀',
            message=f"Your profile will be featured for {duration} hours. Get ready for more matches!",
            data={'action_url': '/dashboard/'}
        )