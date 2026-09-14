from rest_framework import serializers
from features.staffs.models import Staff

class StaffSerializer(serializers.ModelSerializer):
    department_id = serializers.IntegerField(required=False, allow_null=True)
    role_id = serializers.IntegerField(required=False, allow_null=True)
    rank_id = serializers.IntegerField(required=False, allow_null=True)
    stype_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Staff
        fields = '__all__'
        depth = 2
