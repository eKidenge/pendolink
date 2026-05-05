from django.db import models
from django.conf import settings

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    duration_days = models.IntegerField()
    price_kes = models.DecimalField(max_digits=10, decimal_places=2)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Features
    daily_likes = models.IntegerField(default=100)
    can_see_who_liked = models.BooleanField(default=False)
    unlimited_chats = models.BooleanField(default=False)
    priority_matching = models.BooleanField(default=False)
    expanded_radius = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'billing_subscription_plans'
        app_label = 'billing'
    
    def __str__(self):
        return f"{self.name} - KES {self.price_kes}"

class UserSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    
    # Payment info
    payment_method = models.CharField(max_length=50)  # mpesa, card
    payment_reference = models.CharField(max_length=200)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'billing_user_subscriptions'
        app_label = 'billing'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('card', 'Card'),
        ('balance', 'Balance'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # For M-Pesa
    mpesa_receipt_number = models.CharField(max_length=50, null=True, blank=True)
    mpesa_phone_number = models.CharField(max_length=15, null=True, blank=True)
    
    # For card
    card_last4 = models.CharField(max_length=4, null=True, blank=True)
    stripe_payment_intent = models.CharField(max_length=100, null=True, blank=True)
    
    description = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'billing_transactions'
        app_label = 'billing'
        ordering = ['-created_at']

class BoostPurchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='boosts')
    duration_hours = models.IntegerField()
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'billing_boost_purchases'
        app_label = 'billing'
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]