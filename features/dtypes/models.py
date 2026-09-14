from django.db import models

class Dtype(models.Model):

    class Meta:
        db_table = "document_types"

    dtype_id = models.CharField(unique=True, null=False, max_length=20)
    dtype_name = models.CharField(unique=True, null=False, max_length=50)