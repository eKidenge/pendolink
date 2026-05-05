from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, UserSubscription, Transaction, BoostPurchase

class PaymentService:
    def __init__(self, user):
        self.user = user
    
    def create_transaction(self, amount, payment_method, description, metadata=None):
        """Create a transaction record"""
        return Transaction.objects.create(
            user=self.user,
            amount=amount,
            currency='KES',
            payment_method=payment_method,
            status='pending',
            description=description,
            metadata=metadata or {}
        )
    
    def complete_transaction(self, transaction_id, receipt_number=None):
        """Mark transaction as completed"""
        try:
            transaction = Transaction.objects.get(id=transaction_id, user=self.user)
            transaction.status = 'completed'
            transaction.completed_at = timezone.now()
            if receipt_number:
                transaction.mpesa_receipt_number = receipt_number
            transaction.save()
            return True
        except Transaction.DoesNotExist:
            return False
    
    def purchase_boost(self, duration_hours, payment_method):
        """Purchase a profile boost"""
        # Calculate price (simplified)
        if duration_hours == 1:
            price = 99
        elif duration_hours == 6:
            price = 499
        else:
            price = 1499
        
        # Create transaction
        transaction = self.create_transaction(
            amount=price,
            payment_method=payment_method,
            description=f"{duration_hours} hour profile boost"
        )
        
        # Create boost purchase
        boost = BoostPurchase.objects.create(
            user=self.user,
            duration_hours=duration_hours,
            end_time=timezone.now() + timedelta(hours=duration_hours),
            transaction=transaction
        )
        
        return {'success': True, 'boost_id': boost.id, 'transaction_id': transaction.id}

class SubscriptionService:
    def __init__(self, user):
        self.user = user
    
    def create_subscription(self, plan_id, payment_method):
        """Create a new subscription"""
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            
            # Calculate end date
            end_date = timezone.now() + timedelta(days=plan.duration_days)
            
            # Create transaction
            transaction = Transaction.objects.create(
                user=self.user,
                amount=plan.price_kes,
                currency='KES',
                payment_method=payment_method,
                status='completed',
                description=f"{plan.name} subscription",
                completed_at=timezone.now()
            )
            
            # Create subscription
            subscription = UserSubscription.objects.create(
                user=self.user,
                plan=plan,
                end_date=end_date,
                payment_method=payment_method,
                payment_reference=f"SUB_{transaction.id}"
            )
            
            # Update user premium status
            self.user.is_premium = True
            self.user.premium_until = end_date
            self.user.save()
            
            # Send notification
            from apps.notifications.services import NotificationService
            NotificationService.send_premium_notification(self.user, plan.name)
            
            return {'success': True, 'subscription_id': subscription.id}
            
        except SubscriptionPlan.DoesNotExist:
            return {'success': False, 'error': 'Invalid plan'}
    
    def cancel_subscription(self):
        """Cancel current subscription"""
        subscription = UserSubscription.objects.filter(
            user=self.user,
            is_active=True
        ).first()
        
        if subscription:
            subscription.is_active = False
            subscription.auto_renew = False
            subscription.save()
            
            self.user.is_premium = False
            self.user.save()
            
            return {'success': True}
        
        return {'success': False, 'error': 'No active subscription'}

class MpesaService:
    def __init__(self):
        # Initialize M-Pesa API credentials
        self.consumer_key = 'YOUR_CONSUMER_KEY'
        self.consumer_secret = 'YOUR_CONSUMER_SECRET'
        self.passkey = 'YOUR_PASSKEY'
        self.shortcode = 'YOUR_SHORTCODE'
    
    def initiate_payment(self, user, amount, phone_number):
        """Initiate M-Pesa STK Push payment"""
        # For development, simulate success
        transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            currency='KES',
            payment_method='mpesa',
            status='pending',
            description='M-Pesa payment',
            mpesa_phone_number=phone_number
        )
        
        return {'success': True, 'transaction_id': transaction.id, 'message': 'STK push sent to your phone'}
    
    def handle_callback(self, callback_data):
        """Handle M-Pesa callback"""
        # Process callback data
        # Update transaction status
        pass