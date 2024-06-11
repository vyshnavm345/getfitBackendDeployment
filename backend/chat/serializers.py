from rest_framework import serializers
from .models import ChatMessage, Notification

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__' 
        
class NotificationSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    sender = serializers.SerializerMethodField()
    sender_id = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = [ 'message', 'sender', 'timestamp', 'sender_id']
        
    def get_sender(self, obj):
        return obj.sender.fullname()
    
    def get_sender_id(self, obj):
        return obj.sender.id