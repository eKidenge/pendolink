from rest_framework import serializers
from .models import Location, GeographicRegion, LocationHistory

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'town', 'sub_county', 'latitude', 'longitude', 'is_active', 'last_updated', 'max_match_distance']
        read_only_fields = ['last_updated']

class GeographicRegionSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True)
    
    class Meta:
        model = GeographicRegion
        fields = ['id', 'name', 'region_type', 'parent', 'center_latitude', 'center_longitude', 'population_density', 'distance']

class LocationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationHistory
        fields = ['id', 'city', 'town', 'latitude', 'longitude', 'timestamp']
        read_only_fields = ['timestamp']