
from django.db import models
# from django.conf import settings
from user.models import UserAccount

class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255)
    sender = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, blank=True)
    # data = models.BinaryField(blank=True)
    media_file = models.FileField(upload_to="chat/media", blank=True)  # For audio/video
    image = models.ImageField(upload_to="chat/images", blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        if self.type == "text":
            return f"{self.sender.fullname()}: {self.message[:20]}"
        else:
            return f"{self.sender.fullname()}: Sent a {self.type} message"
    
class Notification(models.Model):
    recipient = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    sender = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} to {self.recipient}: {self.message}"