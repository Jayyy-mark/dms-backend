from django.db import models
from django.utils import timezone

class Rank(models.Model):
    
    rank_id = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )
    rank_name = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ranks"
        
    def __str__(self):
        return self.rank_name