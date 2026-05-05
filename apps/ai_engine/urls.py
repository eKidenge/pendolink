from django.urls import path
from .views import AIRecommendationView, CompatibilityCheckView

urlpatterns = [
    path('recommendations/', AIRecommendationView.as_view(), name='recommendations'),
    path('compatibility/', CompatibilityCheckView.as_view(), name='compatibility'),
]