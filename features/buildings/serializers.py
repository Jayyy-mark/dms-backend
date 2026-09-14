from rest_framework import serializers
from features.buildings.models import Building

class BuildingSerializer(serializers.ModelSerializer):

    class Meta:
        model=Building
        fields='__all__'
