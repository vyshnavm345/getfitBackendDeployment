from django.urls import path
from .views import (
    GetChatMessages,
    GetNotifications,
    GetOnlineUserIDs
)

urlpatterns = [
    
    path("getMessages/<str:room_id>/", GetChatMessages.as_view()),
    path("getNotifications/", GetNotifications.as_view()),
    path("getOnlineUserIDs/", GetOnlineUserIDs.as_view()),
    
]
