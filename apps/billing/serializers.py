from rest_framework import serializers
from decimal import Decimal
from .models import SubscriptionPlan, UserSubscription, Transaction, BoostPurchase

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    price_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'duration_days', 'price_kes', 'price_usd', 'daily_likes',
            'can_see_who_liked', 'unlimited_chats', 'priority_matching', 'expanded_radius',
            'is_active', 'price_display', 'created_at'
        ]
    
    def get_price_display(self, obj):
        return f"KES {obj.price_kes}"

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'plan', 'plan_details', 'start_date', 'end_date',
            'is_active', 'auto_renew', 'days_remaining', 'is_expired', 'created_at'
        ]
        read_only_fields = ['user', 'start_date', 'created_at']
    
    def get_days_remaining(self, obj):
        from django.utils import timezone
        if obj.end_date:
            delta = obj.end_date - timezone.now()
            return max(0, delta.days)
        return 0
    
    def get_is_expired(self, obj):
        from django.utils import timezone
        return obj.end_date and obj.end_date < timezone.now()

class TransactionSerializer(serializers.ModelSerializer):
    formatted_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'amount', 'currency', 'payment_method', 'status',
            'mpesa_receipt_number', 'mpesa_phone_number', 'card_last4',
            'description', 'metadata', 'created_at', 'completed_at', 'formatted_amount'
        ]
        read_only_fields = ['user', 'created_at']
    
    def get_formatted_amount(self, obj):
        return f"{obj.currency} {obj.amount}"

class MpesaPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('1'))
    phone_number = serializers.CharField(max_length=15)
    
    def validate_phone_number(self, value):
        import re
        cleaned = re.sub(r'\D', '', value)
        if len(cleaned) == 9:
            cleaned = '254' + cleaned
        if not cleaned.startswith('254') or len(cleaned) != 12:
            raise serializers.ValidationError("Invalid phone number format")
        return cleaned

class CardPaymentSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=19)
    expiry_month = serializers.IntegerField(min_value=1, max_value=12)
    expiry_year = serializers.IntegerField()
    cvc = serializers.CharField(max_length=4)
    cardholder_name = serializers.CharField(max_length=100)
    
    def validate_expiry_year(self, value):
        from django.utils import timezone
        if value < timezone.now().year:
            raise serializers.ValidationError("Card has expired")
        return value