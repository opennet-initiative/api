from rest_framework_gis import serializers 
from oni_model.models import AccessPoint

class AccessPointSerializer(serializers.GeoModelSerializer):
    class Meta:
        model = AccessPoint
    

