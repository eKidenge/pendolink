from django.urls import path
from .views import (
    SubscriptionPlansView, SubscribeView, CancelSubscriptionView,
    MpesaPaymentView, MpesaCallbackView, PurchaseBoostView,
    TransactionHistoryView, MySubscriptionView
)

urlpatterns = [
    path('', SubscriptionPlansView.as_view(), name='subscription'),  # ADD THIS LINE
    path('plans/', SubscriptionPlansView.as_view(), name='plans'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('cancel/', CancelSubscriptionView.as_view(), name='cancel'),
    path('mpesa/pay/', MpesaPaymentView.as_view(), name='mpesa-pay'),
    path('mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa-callback'),
    path('boost/purchase/', PurchaseBoostView.as_view(), name='purchase-boost'),
    path('transactions/', TransactionHistoryView.as_view(), name='transactions'),
    path('my-subscription/', MySubscriptionView.as_view(), name='my-subscription'),
]