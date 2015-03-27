from django.db import models
from django.contrib.gis.db import models as gismodels


class AccessPoint(models.Model):
    main_ip=models.IPAddressField(primary_key=True)
    post_address=models.TextField()
    antenna=models.TextField()
    position=gismodels.PointField(default=None)
    objects = gismodels.GeoManager()
    owner=models.TextField()
    device_model=models.TextField()

