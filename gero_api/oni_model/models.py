from django.db import models

# Create your models here.
class Node(models.Model):
    ip=models.IPAddressField(primary_key=True)
    post_address=models.TextField()
    antenna=models.TextField()
    lat=models.FloatField()
    long=models.FloatField()
    owner=models.TextField()
    device=models.TextField()

