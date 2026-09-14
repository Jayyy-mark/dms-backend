from rest_framework import serializers
from features.departments.models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Department
        fields = '__all__'
        depth = 1
