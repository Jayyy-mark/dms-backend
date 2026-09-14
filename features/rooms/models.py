from django.utils import timezone
from django.db import models
from features.buildings.models import Building

class Room(models.Model):
    
    room_id = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )

    room_no = models.IntegerField(default=0)
    
    room_name = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )

    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="rooms",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rooms"

    def __str__(self):
        return self.room_name