from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
# from django.contrib.gis.db.models.functions import Distance  # Comment out
# from django.contrib.gis.geos import Point  # Comment out
from django.db.models import Q, F
from math import radians, sin, cos, acos, sqrt
from .models import Location, GeographicRegion
from .serializers import LocationSerializer, GeographicRegionSerializer
from apps.matching.services import update_user_matching_radius

# Helper function to calculate distance between two points (Haversine formula)
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points"""
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

class UpdateLocationView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationSerializer
    
    def get_object(self):
        location, created = Location.objects.get_or_create(user=self.request.user)
        return location
    
    def perform_update(self, serializer):
        location = serializer.save(user=self.request.user)
        # Trigger matching radius update
        update_user_matching_radius(self.request.user)

class NearbyRegionsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user_location = Location.objects.filter(user=request.user).first()
        if not user_location or not (user_location.latitude and user_location.longitude):
            return Response({'error': 'Location not set'}, status=status.HTTP_400_BAD_REQUEST)
        
        radius = float(request.GET.get('radius', 50))
        
        # Calculate distances manually (simplified)
        nearby_regions = []
        for region in GeographicRegion.objects.filter(is_active=True):
            if region.center_latitude and region.center_longitude:
                distance = haversine_distance(
                    float(user_location.latitude), float(user_location.longitude),
                    float(region.center_latitude), float(region.center_longitude)
                )
                if distance <= radius:
                    nearby_regions.append({
                        'id': region.id,
                        'name': region.name,
                        'region_type': region.region_type,
                        'distance': distance
                    })
        
        # Sort by distance
        nearby_regions.sort(key=lambda x: x['distance'])
        
        return Response(nearby_regions[:20])

class SearchByLocationView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationSerializer
    
    def get_queryset(self):
        town = self.request.GET.get('town')
        if town:
            return Location.objects.filter(town__icontains=town, is_active=True)
        city = self.request.GET.get('city')
        if city:
            return Location.objects.filter(city__icontains=city, is_active=True)
        return Location.objects.none()