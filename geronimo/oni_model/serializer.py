from rest_framework import serializers
from oni_model.models import AccessPoint

class AccessPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPoint
    

