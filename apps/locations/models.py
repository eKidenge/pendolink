from django.db import models
# from django.contrib.gis.db import models as gis_models  # Comment this out
from django.conf import settings

class Location(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='location')
    city = models.CharField(max_length=100)
    town = models.CharField(max_length=100, db_index=True)
    sub_county = models.CharField(max_length=100, blank=True)
    
    # Replace GIS PointField with regular fields
    # coordinates = gis_models.PointField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Geo accuracy
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Distance preferences
    max_match_distance = models.IntegerField(default=50)  # km
    
    class Meta:
        db_table = 'locations'
        indexes = [
            models.Index(fields=['town', 'is_active']),
            models.Index(fields=['city']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.town}, {self.city}"

class LocationHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    # coordinates = gis_models.PointField()  # Comment out
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'location_history'
        ordering = ['-timestamp']

class GeographicRegion(models.Model):
    REGION_TYPES = [
        ('city', 'City'),
        ('town', 'Town'),
        ('sub_county', 'Sub-County'),
    ]
    
    name = models.CharField(max_length=100)
    region_type = models.CharField(max_length=20, choices=REGION_TYPES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    # geometry = gis_models.PolygonField(null=True, blank=True)  # Comment out
    # center_point = gis_models.PointField()  # Comment out
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    population_density = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'geographic_regions'
    
    def __str__(self):
        return f"{self.name} ({self.region_type})"