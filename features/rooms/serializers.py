from rest_framework import serializers
from features.rooms.models import Room

class RoomSerializer(serializers.ModelSerializer):
    building_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Room
        fields = '__all__'
        depth = 1
