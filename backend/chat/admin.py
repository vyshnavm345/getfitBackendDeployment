from django.contrib import admin
from .models import ChatMessage, Notification
# Register your models here.
admin.site.register(ChatMessage)
admin.site.register(Notification)