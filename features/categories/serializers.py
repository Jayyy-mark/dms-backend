from rest_framework import serializers
from features.categories.models import Category


class CategorySerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Category
        fields = "__all__"
        depth = 3
