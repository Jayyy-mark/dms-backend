from django.db import models
from django.utils import timezone
class Role(models.Model):
    
    role_id = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )
    role_name = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"
        
    def __str__(self):
        return self.role_name