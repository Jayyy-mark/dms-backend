from django.db import models

class Building(models.Model):

    class Meta:
        db_table="buildings"

    building_id = models.CharField(max_length=10, unique=True, null=False)
    building_name = models.CharField(max_length=50, unique=True, null=False)

    created_time = models.DateTimeField(auto_now_add=True)