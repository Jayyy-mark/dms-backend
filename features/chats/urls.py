from django.urls import path
from .views import chat, upload_chat_document

urlpatterns = [
    path('chat/', chat),
    path('chat/upload/', upload_chat_document),
]
