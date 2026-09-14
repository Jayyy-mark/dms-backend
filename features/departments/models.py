from django.db import models
from features.rooms.models import Room
from django.utils import timezone

class Department(models.Model):
    
    department_id = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )
    department_name = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )

    #Foreignkey
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="departments",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "departments"
        
    def __str__(self):
        return self.department_name