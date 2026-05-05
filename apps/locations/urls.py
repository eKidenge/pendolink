from django.urls import path
from .views import UpdateLocationView, NearbyRegionsView, SearchByLocationView

urlpatterns = [
    path('update/', UpdateLocationView.as_view(), name='update-location'),
    path('nearby-regions/', NearbyRegionsView.as_view(), name='nearby-regions'),
    path('search/', SearchByLocationView.as_view(), name='search-location'),
]