from rest_framework.views import APIView
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view 
from django.core.exceptions import ValidationError

from rest_framework_simplejwt.tokens import RefreshToken
from fitness_program.serializers import FitnessProgramSerializer
from fitness_program.models import FitnessProgram
from .permissions.admin_permission import IsAdminUser, IsNotBlocked

# from django.dispatch import user_authenticated
# from django.dispatch import user_authenticated

from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    UserWithProfileSerializer,
    ProfileSerializer,
    UserFollowedProgramSerializer,
)
from .models import Profile, UserAccount, FollowedPrograms
from django.shortcuts import get_object_or_404
import time
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings
import json
from trainer.serializers import TrainerSerializer

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        data = request.data
        serializer = UserCreateSerializer(data=data)
        if not serializer.is_valid():
            error_messages = ""
            for field, messages in serializer.errors.items():
                for message in messages:
                    error_messages += f"{message}. \n"
            return Response(
                {"error_message": error_messages.strip()},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.create(serializer.validated_data)
        user_data = UserSerializer(user)

        user = UserAccount.objects.get(email=user.email)
        token = RefreshToken.for_user(user).access_token

        # current_site = get_current_site(request).domain
        # relative_link = reverse("email_verification")
        # absurl = "http://" + current_site + relative_link + "?token=" + str(token)
        absurl = "https://getfittoday.xyz/verify/" + str(token)
        # absurl = "http://127.0.0.1:3000/verify/" + str(token)
        
        email_body = (
            "Hi "
            + user.first_name
            + "Use the link below to verify your email \n"
            + absurl
        )
        data = {
            "email_body": email_body,
            "to_email": user.email,
            "email_subject": "Veryfy your email",
        }
        print("the data is : ", data)
        frontend_domain = request.headers.get('Origin')
        print("This is the frontend domain : ", frontend_domain)
        
        
        Util.send_email(data)
        print("mail send")

        return Response(
            {"message": "Verification link sent to your email"},
            status=status.HTTP_201_CREATED
        )
        


class Verify_email(generics.GenericAPIView):
    def post(self, request):
        data = json.loads(request.body)
        token = data.get("token")
        print("This is the recieved Token:",token)
        print("This is the secret key : ",settings.SECRET_KEY)
        
        try:
            payload =jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = UserAccount.objects.get(id=payload['user_id'])
            # print("the user is :", user)
            if not user.is_verified:
                print("inside verified")
                user.is_verified = True
                user.save()
            else:
                return Response({"Message":"Account already active"}, status=status.HTTP_208_ALREADY_REPORTED)
            # user = UserSerializer(user)
            # return Response(user.data, status=status.HTTP_201_CREATED)
            print("sending message")
            return Response({"Message":"Account Activated \n Now Log in using your credentials"}, status=status.HTTP_201_CREATED)
        except jwt.ExpiredSignatureError as e:
            return Response({"error" : "Activation Link Expired"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as e:
            print("Error decoding token:", e)
            return Response({"error" : "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST)


class RetriveUserView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBlocked]

    def get(self, request):
        user = request.user
        if user.is_verified:
            user = UserSerializer(user)

            return Response(user.data, status=status.HTTP_200_OK)
        if user.blocked:
            return Response({"message":"You have been temporarly blocked by the Admin"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"message":"Email not Verified"}, status=status.HTTP_401_UNAUTHORIZED)

# add a decorater here to let only the once in the verified group to access
class Retrive_full_user_data(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        print("retreving userdata")
        try:
            user = request.user
            if user.blocked:
                return Response({"message":"You have been temporarly blocked by the Admin"}, status=status.HTTP_401_UNAUTHORIZED)
            if user.is_verified:
                user = UserWithProfileSerializer(user)
                return Response(user.data, status=status.HTTP_200_OK)
            return Response({"message":"Email not Verified"}, status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception as e:
            print("error : ", str(e))
            return Response({"message": "An error occurred while retrieving user data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
def update_user_profile(request):
    data = request.data.copy()
    profile_data = {
        "height": data.get("height"),
        "weight": data.get("weight"),
        "body_fat": data.get("body_fat"),
        "age": data.get("age"),
        "phone": data.get("phone"),
    }
    user_data = {
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "email": data.get("email"),
    }
    print("this is the user data", user_data)
    print("this is the profile data", profile_data)
    profile_picture = request.data.get("profile_picture")
    if profile_picture != "null":
        user_data["profile_picture"] = profile_picture

    user_id = request.data.get("id")
    user = UserAccount.objects.get(id=user_id)
    user_serializer = UserSerializer(user, data=user_data, partial=True)

    if user_serializer.is_valid():
        print("serializer is valid")
        user_instance = user_serializer.save()
        profile_instance, created = Profile.objects.get_or_create(user=user_instance)
        
        cleaned_profile_data = {}
        for key, value in profile_data.items():
            if value != 'null':  # Skip null values
                cleaned_profile_data[key] = value
        print("this is the cleaned profile data", cleaned_profile_data)
        
        profile_serializer = ProfileSerializer(
            profile_instance, data=cleaned_profile_data, partial=True
        )
        if profile_serializer.is_valid():
            print("valid profile serializer")
            profile_serializer.save()
            return Response(
                {"message": "User profile updated successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            print("profile serializer error : ", profile_serializer.errors)
    print("This is the reason ", user_serializer.errors)
    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetFollowedPrograms(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        try:
            print("inside GetFollowedPrograms")
            user = request.user
            if user.is_verified:
                programs = FollowedPrograms.objects.filter(user=user)
                print("these are the followed programms", programs)
                serializer = UserFollowedProgramSerializer(programs, many=True)
                print(serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response("User is not verified", status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class GetUserById(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, id):
        try:
            user = UserAccount.objects.get(id=id)
            if user.is_verified:
                user = UserWithProfileSerializer(user)
                print("this is the user by id", user.data)
                return Response(user.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
# follow a particular program
# class FollowProgram(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     def get(self, request, id):
#         try:
#             program = FitnessProgram.objects.get(id=id)
#             user = request.user
#             if FollowedPrograms.objects.filter(user=user, program=program).exists():
#                 return Response({'message': 'You are already subscribed to this program'}, status=status.HTTP_200_OK)
#             else:
#                 FollowedPrograms.objects.create(user=user, program=program)
#             return Response({'message': 'Successfully subscribed to the Programme'}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


# follow a program
class FollowProgram(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            program = get_object_or_404(FitnessProgram, id=id)
            user = request.user
            followed_program, created = FollowedPrograms.objects.get_or_create(user=user)
            if program in followed_program.program.all():
                return Response({'message': 'You are already subscribed to this program'}, status=status.HTTP_200_OK)
            else:
                followed_program.program.add(program)
                return Response({'message': 'Successfully subscribed to the Programme'}, status=status.HTTP_200_OK)
        except FitnessProgram.DoesNotExist:
            return Response({'message': 'Program not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# unfollow a program
class UnfollowProgram(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            program = get_object_or_404(FitnessProgram, id=id)
            user = request.user
            followed_program = FollowedPrograms.objects.get(user=user)
            if program in followed_program.program.all():
                followed_program.program.remove(program)
                return Response({'message': 'Successfully unsubscribed from the program'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You are not subscribed to this program'}, status=status.HTTP_200_OK)
        except FitnessProgram.DoesNotExist:
            return Response({'message': 'Program not found'}, status=status.HTTP_404_NOT_FOUND)
        except FollowedPrograms.DoesNotExist:
            return Response({'message': 'You are not subscribed to any program'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class GetUserTrainers(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        try:
            user = request.user
            if user.is_verified:
                programs = FollowedPrograms.objects.filter(user=user)
                trainers = set()
                for followed_program in programs:
                    for program in followed_program.program.all():
                    # Add the trainer of each followed program to the set of trainers
                        trainers.add(program.trainer)
                    
                
                serializer = TrainerSerializer(trainers, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response("User is not verified", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("error", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
        
class GetUserContacts(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            if user.is_verified:
                programs = FollowedPrograms.objects.filter(user=user)
                trainers = set()
                for followed_program in programs:
                    for program in followed_program.program.all():
                        # Add the trainer of each followed program to the set of trainers
                        trainers.add(program.trainer)
                users = []
                for trainer in trainers:
                    # Change here: Get the first instance of UserAccount
                    user_instance = UserAccount.objects.filter(trainer_profile=trainer).first()
                    if user_instance:
                        users.append(user_instance)
                # Change here: Pass users list to serializer, not queryset
                serializer = UserSerializer(users, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response("User is not verified", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("error", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


# class UserLogout(APIView):
#     print("request received")
#     permission_classes = [permissions.IsAuthenticated]
#     
#     def post(self, request):
#         print("The request is : ", request)
#         try:
#             user = request.user
#             user.logged_in = False
            # print("The user is " , user)
            # print("The user logged status is " , user.logged_in)
#             return Response("User logged Out", status=status.HTTP_200_OK)
#         except Exception as e:
#             print("error : ", str(e))
#             return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class UserLogout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print("the user is being logged out")
        try:
            user = request.user
            user.logged_in = False
            user.save()
            print("The user is " , user)
            print("The user logged status is " , user.logged_in)
            return Response("User logged out", status=status.HTTP_200_OK)
        except Exception as e:
            print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
        
class GetUserCount(APIView):
    def get(self, request):
        try:  
            count = UserAccount.objects.exclude(is_superuser=True).count()
            return Response({count}, status=status.HTTP_200_OK)
        except Exception as e:
            print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

class GetLoggedInUsers(APIView):
    def get(self, request):
        try:
            print("Total user called")
            online_users = UserAccount.objects.filter(is_trainer=False, logged_in=True, is_superuser=False)
            print("Total user : ", online_users)
            serializer = UserSerializer(online_users, many=True)
            print("serialized data : ", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
        
class GetAllUsers(APIView):
    def get(self, request):
        try:
            # users = UserAccount.objects.all()
            users = UserAccount.objects.exclude(is_superuser=True).exclude(is_trainer=True).order_by('-id')
            serializer = UserSerializer(users, many=True)
            print("serialized data : ", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
# Block and unblock user
class ChangeUserAccess(APIView):
    # only admin can access these methods
    permission_classes = [IsAdminUser]
    def get(self, request, id):
        try:
            user = UserAccount.objects.get(id=id)
            user.blocked = not user.blocked
            user.save()
            message = "User Blocked" if user.blocked else "User Unblocked"
            return Response({"message": message}, status=status.HTTP_200_OK)
        except Exception as e:
            print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)        
