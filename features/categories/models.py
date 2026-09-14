from django.db import models


class Category(models.Model):

    class Meta:
        db_table = "categories"

    category_id = models.CharField(max_length=20, null=False, unique=True, default="-")
    category_name = models.CharField(max_length=300, null=False, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="childrens",
        null=True,
        blank=True,
    )
