
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage, Notification
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async 
from asgiref.sync import async_to_sync
import jwt
from django.conf import settings
from user.models import UserAccount, Profile
from channels.layers import get_channel_layer

from django.core.files.base import ContentFile
import base64

from .utils import getTrainerContacts, getUserContacts

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # access_token = self.scope['url_route']['kwargs']['access_token']
        self.room_group_name = f"chat_{self.room_name}"
        self.user = None
        self.receiver = None
        

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        print('The text data is : ',text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        access_token = text_data_json["access_token"]
        message_type = text_data_json["type"]
        receiver = text_data_json["receiver"]
        fdata = text_data_json["data"]
        print("The data in the begning", fdata)
        self.receiver = receiver
        print("The token : ",access_token)
        try:
            decoded_token =jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            user = await sync_to_async(UserAccount.objects.get)(id=decoded_token['user_id'])
            print("The user is : ",user)
            # Now you have the user object, do whatever you need with it
        except jwt.ExpiredSignatureError:
            # Handle token expiration error
            print("error")
            pass
        except jwt.InvalidTokenError:
            # Handle invalid token error
            print("error")
            pass
        
        if message_type == "text":
            # saving the message to the database
            new_message = await sync_to_async(ChatMessage.objects.create)(
                room_name=self.room_name,
                sender=user,
                message=message
            )
            
            # message for sendng to the group
            message_data = {
                'id': new_message.id,  # Include the message ID
                'sender': user.id,  
                'receiver': receiver,
                "room_name": self.room_name,
                'message': new_message.message,
                'type': message_type,
                'timestamp': str(new_message.timestamp),  # Convert timestamp to string
            }
            print("the message is being sent", message_data)
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": message_data}
            )
            print("the message is broadcasted to the room: ", self.room_group_name)
        elif message_type in ["image", "audio", "video"]:
            print("the attachment is multimedia")
            data = text_data_json.get("data")
            image_base64 = data

            print("data : ",image_base64)# Check if data key exists
            
            if data:
                image_data = base64.b64decode(image_base64)
                image_file = ContentFile(image_data, name="image.png")
                # Validate file size and type
                # ... (validation logic) ...
                # saving the multimedia message to the database
                new_message = await sync_to_async(ChatMessage.objects.create)(
                    room_name=self.room_name,
                    sender=user,
                    message=message,  # Or a descriptive message about the media
                    type=message_type,
                    image=image_file if message_type == "image" else None,
                    media_file=data if message_type != "image" else None
                )
                
                # multimedia message for sendng to the group
                message_data = {
                    'id': new_message.id,
                    'sender': user.id,
                    'receiver': receiver,
                    "room_name": self.room_name,
                    'message': new_message.message,
                    'type': message_type,  # Multimedia message type
                    'timestamp': str(new_message.timestamp),
                    "data": new_message.image.url if message_type == "image" else new_message.media_file.url
                    # Include additional fields for multimedia data (e.g., filename, size)
                    # 'sender': user.username,  # Or other relevant sender information
                }
                await self.channel_layer.group_send(  # Send message to room group
                    self.room_group_name,
                    {
                        'type': 'chat_message',  # Event type for consumers to handle
                        'message': message_data
                    }
                )
            else:
                print("Error: Missing data for multimedia message")
            
            
        print("the recepient id : ", receiver)
        recepient = await sync_to_async(UserAccount.objects.get)(id=receiver)
        print("the user name is : ", user.id,   user.fullname(), "receiver : ", recepient, recepient.id, recepient.fullname(), recepient.logged_in)
        self.username = user.fullname()

        # Send message to room group
        
        print("successfully completed")

        if recepient.logged_in:
            print("Notification is being sent")
            print("The message data being passed into send_notification is : ", message_data)
            # Send notification to notification group
            await self.send_notification(message_data)
        else:
            await sync_to_async(Notification.objects.create)(
                recipient=recepient,
                message=message_data["message"],
                sender=user,
                timestamp=message_data["timestamp"]
            )

# Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
        
    async def send_notification(self, message_data):
        # Get the channel layer
        channel_layer = get_channel_layer()

        # Construct the notification message
        notification_message = {
            "type": "notification.message",
            "message": message_data["message"],
            "sender": self.username,
            "timestamp": message_data["timestamp"],
            "category" : 'message',
            'receiver': self.receiver,
            "sender_id": message_data['sender']
            
        }
        
        # Construct the group name with user.id
        group_name = f"chat_link{message_data['receiver']}"
        # print("the groupname is", group_name)
        # print('sending notification')
        # print("message data : ", message_data)
        # Send the notification message to the notification group
        await channel_layer.group_send(
            group_name,
            notification_message
        )
        print('notificaion sent :', notification_message)
        
        
        
        
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = None
        
        # Join the notification group
        print("connecting to the room and the room group name is", self.room_group_name)
        text = self.room_group_name
        id = text.replace("chat_link",'')
        print(int(id))
        online_user = await sync_to_async(UserAccount.objects.get)(id=int(id))
        self.user = online_user
        
        if self.user.is_verified:
        
            print(f"the {self.user.fullname()} is logged in")
            if self.user.is_trainer:
                contacts = await getTrainerContacts(self.user)
                print("trainer contacts received")
            else:
                contacts = await getUserContacts(self.user)
                print("user contacts received")
                
            # print("the contacts are : ", contacts)
            for user in contacts:
                await self.send_onlineStatus(user.id, message="user Online")
                
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        print(f"the {self.user.fullname()} is logging out")
        self.user.logged_in = False
        save_user = sync_to_async(self.user.save)
        # await save_user()
        if self.user.is_trainer:
            contacts = await getTrainerContacts(self.user)
            print("trainer contacts received")
        else:
            contacts = await getUserContacts(self.user)
            print("user contacts received")
            
        for user in contacts:
            await self.send_onlineStatus(user.id, message="user Offline")
        # Leave the notification group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_onlineStatus(self, user_id, message):
        # Get the channel layer
        channel_layer = get_channel_layer()

        receiver = await sync_to_async(UserAccount.objects.get)(id=user_id)
        # Construct the notification message
        print("The receiver and their id are : ", receiver, receiver.id)
        notification_message = {
            "type": "notification.message",
            "message": message,
            "sender": self.user.id,
            "sender_id": self.user.id,
            "category": 'status',
            "receiver" : receiver.id,
        }
        
        # if self.user.is_trainer:
        #     print(f"the {self.user.fullname()} is a trainer")
        # else:
        #     print(f"the {self.user.fullname()} is a subscriber")
        
        
        # Construct the group name with user.id
        group_name = f"chat_link{user_id}"
        print("THe group name is ",group_name)
        await channel_layer.group_send(
            group_name,
            notification_message
        )
        print('Status notificaion sent :', notification_message)
    
    # Receive message from room group
    async def notification_message(self, event):
        # Send message to WebSocket
        # id = event['receiver']
        # user = UserAccount.objects.get(id=int(id))
        print("inside notification_message method", event)
        get_user = sync_to_async(UserAccount.objects.get)
        user = await get_user(id=int(event['receiver']))
        print("The latest online user is : ", user)
        # profile = Profile.objects.get(user=user)
        get_profile = sync_to_async(Profile.objects.get)
        profile = await get_profile(user=user)
        # print("the profile : ", profile)
        
        user_ids = profile.online_user_ids
        print("User ids are fetched")
        print("Current online users : ", user_ids)
        new_user_id = {"sender_id": event['sender']}
        
        
        if event['message'] == 'user Online':
            if new_user_id not in user_ids:
                user_ids.append(new_user_id)
        elif event['message'] == 'user Offline':
            if new_user_id in user_ids:
                user_ids.remove(new_user_id)
            
        print("the new user id : ", new_user_id)
        print("Updated online users : ", user_ids)
        
        profile.online_user_ids = user_ids
        save_profile = sync_to_async(profile.save)
        await save_profile()
        
        print("sending notificaion to the frontend")
        await self.send(text_data=json.dumps({
            'payload': event['message'],
            "sender": event['sender'],
            "sender_id" : event['sender_id'],
            "type": event['type'],
            "category" : event['category'],
            
        }))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
# import json

# from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import ChatMessage, Notification
# from django.contrib.auth import get_user_model
# from asgiref.sync import sync_to_async 
# from asgiref.sync import async_to_sync
# import jwt
# from django.conf import settings
# from user.models import UserAccount, Profile
# from channels.layers import get_channel_layer

# from .utils import getTrainerContacts, getUserContacts

# User = get_user_model()


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         # access_token = self.scope['url_route']['kwargs']['access_token']
#         self.room_group_name = f"chat_{self.room_name}"
#         self.user = None
#         self.receiver = None
        

#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#         access_token = text_data_json["access_token"]
#         receiver = text_data_json["receiver"]
#         data = text_data_json["data"]
#         print("the data is : ", data)
#         self.receiver = receiver
#         print("The token : ",access_token)
#         try:
#             decoded_token =jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
#             # user = await sync_to_async(UserAccount.objects.get)(id=decoded_token['user_id'])
#             user = await sync_to_async(UserAccount.objects.get)(id=decoded_token['user_id'])
           
#             print("The user is : ",user)
#             # Now you have the user object, do whatever you need with it
#         except jwt.ExpiredSignatureError:
#             # Handle token expiration error
#             print("error")
#             pass
#         except jwt.InvalidTokenError:
#             # Handle invalid token error
#             print("error")
#             pass
        
#         if user:
#             new_message = await sync_to_async(ChatMessage.objects.create)(
#                 room_name=self.room_name,
#                 sender=user,
#                 message=message
#             )
            
            
#             message_data = {
#                 'id': new_message.id,  # Include the message ID
#                 'sender': user.id,  
#                 'receiver': receiver,
#                 "room_name": self.room_name,
#                 'message': new_message.message,
#                 'timestamp': str(new_message.timestamp),  # Convert timestamp to string
#             }
#             print("the recepient id : ", receiver)
#             recepient = await sync_to_async(UserAccount.objects.get)(id=receiver)
#             print("the user name is : ", user.id,   user.fullname(), "receiver : ", recepient, recepient.id, recepient.fullname(), recepient.logged_in)
#             self.username = user.fullname()

#             # Send message to room group
            
#             print("the message is broadcasted to the room: ", self.room_group_name)
#             await self.channel_layer.group_send(
#                 self.room_group_name, {"type": "chat.message", "message": message_data}
#             )
#             print("successfully completed")

#             if recepient.logged_in:
#                 print("Notification is being sent")
#                 print("The message data being passed into send_notification is : ", message_data)
#                 # Send notification to notification group
#                 await self.send_notification(message_data)
#             else:
#                 await sync_to_async(Notification.objects.create)(
#                     recipient=recepient,
#                     message=message_data["message"],
#                     sender=user,
#                     timestamp=message_data["timestamp"]
#                 )

#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({"message": message}))
        
#     async def send_notification(self, message_data):
#         # Get the channel layer
#         channel_layer = get_channel_layer()

#         # Construct the notification message
#         notification_message = {
#             "type": "notification.message",
#             "message": message_data["message"],
#             "sender": self.username,
#             "timestamp": message_data["timestamp"],
#             "category" : 'message',
#             'receiver': self.receiver,
#             "sender_id": message_data['sender']
            
#         }
        
#         # Construct the group name with user.id
#         group_name = f"chat_link{message_data['receiver']}"
#         # print("the groupname is", group_name)
#         # print('sending notification')
#         # print("message data : ", message_data)
#         # Send the notification message to the notification group
#         await channel_layer.group_send(
#             group_name,
#             notification_message
#         )
#         print('notificaion sent :', notification_message)
        
        
        
        
# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"
#         self.user = None
        
#         # Join the notification group
#         print("connecting to the room and the room group name is", self.room_group_name)
#         text = self.room_group_name
#         id = text.replace("chat_link",'')
#         print(int(id))
#         online_user = await sync_to_async(UserAccount.objects.get)(id=int(id))
#         self.user = online_user
        
        
#         print(f"the {self.user.fullname()} is logged in")
#         if self.user.is_trainer:
#             contacts = await getTrainerContacts(self.user)
#             print("trainer contacts received")
#         else:
#             contacts = await getUserContacts(self.user)
#             print("user contacts received")
            
#         # print("the contacts are : ", contacts)
#         for user in contacts:
#             await self.send_onlineStatus(user.id, message="user Online")
            
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         print(f"the {self.user.fullname()} is logging out")
#         if self.user.is_trainer:
#             contacts = await getTrainerContacts(self.user)
#             print("trainer contacts received")
#         else:
#             contacts = await getUserContacts(self.user)
#             print("user contacts received")
            
#         for user in contacts:
#             await self.send_onlineStatus(user.id, message="user Offline")
#         # Leave the notification group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def send_onlineStatus(self, user_id, message):
#         # Get the channel layer
#         channel_layer = get_channel_layer()

#         receiver = await sync_to_async(UserAccount.objects.get)(id=user_id)
#         # Construct the notification message
#         print("The receiver and their id are : ", receiver, receiver.id)
#         notification_message = {
#             "type": "notification.message",
#             "message": message,
#             "sender": self.user.id,
#             "sender_id": self.user.id,
#             "category": 'status',
#             "receiver" : receiver.id,
#         }
        
#         # if self.user.is_trainer:
#         #     print(f"the {self.user.fullname()} is a trainer")
#         # else:
#         #     print(f"the {self.user.fullname()} is a subscriber")
        
        
#         # Construct the group name with user.id
#         group_name = f"chat_link{user_id}"
#         print("THe group name is ",group_name)
#         await channel_layer.group_send(
#             group_name,
#             notification_message
#         )
#         print('Status notificaion sent :', notification_message)
    
#     # Receive message from room group
#     async def notification_message(self, event):
#         # Send message to WebSocket
#         # id = event['receiver']
#         # user = UserAccount.objects.get(id=int(id))
#         print("inside notification_message method", event)
#         get_user = sync_to_async(UserAccount.objects.get)
#         user = await get_user(id=int(event['receiver']))
#         print("The latest online user is : ", user)
#         # profile = Profile.objects.get(user=user)
#         get_profile = sync_to_async(Profile.objects.get)
#         profile = await get_profile(user=user)
#         # print("the profile : ", profile)
        
#         user_ids = profile.online_user_ids
#         print("User ids are fetched")
#         print("Current online users : ", user_ids)
#         new_user_id = {"sender_id": event['sender']}
        
        
#         if event['message'] == 'user Online':
#             if new_user_id not in user_ids:
#                 user_ids.append(new_user_id)
#         elif event['message'] == 'user Offline':
#             if new_user_id in user_ids:
#                 user_ids.remove(new_user_id)
            
#         print("the new user id : ", new_user_id)
#         print("Updated online users : ", user_ids)
        
#         profile.online_user_ids = user_ids
#         save_profile = sync_to_async(profile.save)
#         await save_profile()
        
#         print("sending notificaion to the frontend")
#         await self.send(text_data=json.dumps({
#             'payload': event['message'],
#             "sender": event['sender'],
#             "sender_id" : event['sender_id'],
#             "type": event['type'],
#             "category" : event['category'],
            
#         }))
        