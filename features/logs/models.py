from django.db import models
from django.conf import settings  # ✅ use this

class AuditLog(models.Model):
    class Meta:
        db_table = "audit_logs"

    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("LOGIN", "Login"),
        ("ARCHIVE", "Archive"),
        ("RESTORE", "Restore"),
        ("OTHER", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ✅ FIX HERE
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name}"