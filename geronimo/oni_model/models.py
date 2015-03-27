from django.db import models
from django.contrib.gis.db import models as gismodels

# Create your models here.
class Node(models.Model):
    ip=models.IPAddressField(primary_key=True)
    post_address=models.TextField()
    antenna=models.TextField()
    position=gismodels.PointField(default=None)
    objects = gismodels.GeoManager()
    owner=models.TextField()
    device=models.TextField()

