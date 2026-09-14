from django.db import models
from authentication.models import MogUser
from django.conf import settings
from features.shared.helpers.storage import UnicodePreservingStorage

unicode_storage = UnicodePreservingStorage()

class ChatMessage(models.Model):
    role = models.CharField(max_length=10) 
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True
    )

class Document(models.Model):
    file = models.FileField(upload_to="chatbot/", storage=unicode_storage)
    uploaded_at = models.DateTimeField(auto_now_add=True)