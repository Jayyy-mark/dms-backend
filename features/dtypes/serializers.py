from rest_framework import serializers
from features.dtypes.models import Dtype

class DtypeSerializer(serializers.ModelSerializer):

    class Meta:
        model=Dtype
        fields="__all__"