from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .models import ChatMessage, Notification
from .serializers import MessageSerializer, NotificationSerializer
from user.models import Profile
from django.core.serializers import serialize
from django.http import JsonResponse

# Create your views here.
class GetChatMessages(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, room_id):
        try:
            print("The room id is : ", room_id)
            messages = ChatMessage.objects.filter(room_name=room_id).order_by("timestamp")
            # print("The messages are :", messages )
            serializer = MessageSerializer(messages, many=True)
            # print("The serialized messages are :", serializer.data )
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print("The error is : ", e)
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class GetNotifications(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        try:
            user = request.user
            pending_notificaions = Notification.objects.filter(recipient=user, seen=False)
            serializer = NotificationSerializer(pending_notificaions, many=True)
            for notificaion in pending_notificaions:
                notificaion.seen = True
                notificaion.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("The error is : ", e)
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class GetOnlineUserIDs(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        try:
            user = request.user
            profile = Profile.objects.get(user=user)
            user_ids = profile.online_user_ids
            print("The user_ids : ", user_ids)
            
            id_list = [item['sender_id'] for item in user_ids]
            print("The id list : ", id_list)
            
            # # Serialize id_list to JSON format
            # data = serialize('json', id_list)
            # print("The serialized data : ", data)

            return Response({'online_user_ids':  id_list}, status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response("Profile not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("The error is : ", e)
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)