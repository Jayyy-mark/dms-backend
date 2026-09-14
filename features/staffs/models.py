from django.utils import timezone
from django.db import models
from features.departments.models import Department
from features.roles.models import Role
from features.ranks.models import Rank
from features.stypes.models import Stype

class Staff(models.Model):
    
    staff_id = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )
    staff_name = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )
    staff_email = models.EmailField(unique=True)

    staff_address = models.CharField(
        max_length=100,
        unique=False,
        null=False
    )
    staff_ph_number = models.CharField(
        max_length=100,
        unique=True,
        null=False
    )
    staff_gender = models.CharField(
        max_length=10,
        unique=False,
        null=False
    )


    #Foreignkey
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="staffs",
        null=True,
        blank=True
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="staffs",
        null=True,
        blank=True
    )
    rank = models.ForeignKey(
        Rank,
        on_delete=models.CASCADE,
        related_name="staffs",
        null=True,
        blank=True
    )
    stype = models.ForeignKey(
        Stype,
        on_delete=models.CASCADE,
        related_name="staffs",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "staffs"
        
    def __str__(self):
        return self.staff_name