from rest_framework import serializers
from features.locations.models import Location, LocationPhoto


class LocationPhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for multiple photos attached to a location.
    """

    class Meta:
        model = LocationPhoto
        fields = ["id", "photo", "created_at"]


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Location model.
    """
    photos = LocationPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = "__all__"


class LocationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing Location.
    """

    location_name = serializers.CharField(
        required=True, allow_null=False, allow_blank=False
    )

    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)

    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Location
        fields = [
            "location_name",
            "longitude",
            "latitude",
            "description",
            "city",
            "state_division",
            "date",
        ]


class LocationSearchSerializer(serializers.ModelSerializer):
    """
    Serializer for searching and filtering locations.
    """

    location_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    location_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    city = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )

    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    date = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    location_type = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    department_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    class Meta:
        model = Location
        fields = [
            "location_id",
            "location_name",
            "city",
            "latitude",
            "longitude",
            "description",
            "date",
            "department_id",
            "location_type",
        ]
