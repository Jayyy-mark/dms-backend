from django.utils import timezone
from django.db import models

class Stype(models.Model):
    
    stype_id = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )
    stype_name = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stypes"
        
    def __str__(self):
        return self.stype_name