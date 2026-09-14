from enum import unique
from django.db import models
from features.departments.models import Department


class Location(models.Model):

    class Meta:
        db_table = "locations"

    location_id = models.CharField(max_length=20, unique=True, null=False)
    location_name = models.CharField(max_length=225, null=False, blank=False)
    location_type = models.CharField(
        max_length=225, null=True, blank=True, unique=False
    )
    photo = models.FileField(upload_to="locations/", null=True, blank=True)

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    description = models.TextField(null=True, blank=True)

    city = models.CharField(max_length=50, unique=False, null=True, blank=True)
    state_division = models.CharField(
        max_length=50, unique=False, null=True, blank=True
    )

    date = models.DateField(null=False)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="locations",
        null=True,
        blank=True,
    )


class LocationPhoto(models.Model):

    class Meta:
        db_table = "location_photos"

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="photos"
    )
    photo = models.FileField(upload_to="locations/photos/")
    created_at = models.DateTimeField(auto_now_add=True)
