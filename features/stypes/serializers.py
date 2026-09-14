from rest_framework import serializers
from features.stypes.models import Stype

class StypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stype
        fields = '__all__'
