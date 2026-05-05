from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import SubscriptionPlan, UserSubscription, Transaction, BoostPurchase
from .serializers import (
    SubscriptionPlanSerializer, UserSubscriptionSerializer,
    TransactionSerializer, MpesaPaymentSerializer, CardPaymentSerializer
)
from .services import PaymentService, MpesaService, SubscriptionService

class SubscriptionPlansView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionPlanSerializer
    
    def get_queryset(self):
        return SubscriptionPlan.objects.filter(is_active=True)

class SubscribeView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        plan_id = request.data.get('plan_id')
        payment_method = request.data.get('payment_method')
        
        subscription_service = SubscriptionService(request.user)
        result = subscription_service.create_subscription(plan_id, payment_method)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class CancelSubscriptionView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        subscription_service = SubscriptionService(request.user)
        result = subscription_service.cancel_subscription()
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class MpesaPaymentView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MpesaPaymentSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            mpesa_service = MpesaService()
            result = mpesa_service.initiate_payment(
                request.user,
                serializer.validated_data['amount'],
                serializer.validated_data['phone_number']
            )
            
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MpesaCallbackView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        mpesa_service = MpesaService()
        mpesa_service.handle_callback(request.data)
        return Response({'ResultCode': 0, 'ResultDesc': 'Success'})

class PurchaseBoostView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        duration_hours = request.data.get('duration_hours', 1)
        payment_method = request.data.get('payment_method')
        
        payment_service = PaymentService(request.user)
        result = payment_service.purchase_boost(duration_hours, payment_method)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class TransactionHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)[:50]

class MySubscriptionView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSubscriptionSerializer
    
    def get_object(self):
        subscription = UserSubscription.objects.filter(
            user=self.request.user,
            is_active=True
        ).first()
        return subscription