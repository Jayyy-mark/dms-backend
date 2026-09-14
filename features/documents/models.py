from django.db import models
from features.staffs.models import Staff
from features.categories.models import Category
from features.dtypes.models import Dtype
from django.utils import timezone
from features.shared.helpers.storage import UnicodePreservingStorage

unicode_storage = UnicodePreservingStorage()

# Create your models here.
class Document(models.Model):

    class Meta:
        db_table="documents"

    document_id = models.CharField(
        max_length=20,
        unique=True,
        null=False
    )
    document_name = models.CharField(
        max_length=225,
        unique=False,
        null=False
    )
    document = models.FileField(upload_to="documents/", storage=unicode_storage, null=True, blank=True)

    description = models.CharField(max_length=225, unique=False, null=True, blank=True)

    staff = models.ForeignKey(
        Staff,
        related_name="documents",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True
    )

    dtype = models.ForeignKey(
        Dtype,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True
    )

    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    is_recycled = models.BooleanField(default=False)
    recycled_at = models.DateTimeField(null=True, blank=True)

    restore_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    expired_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.document_name