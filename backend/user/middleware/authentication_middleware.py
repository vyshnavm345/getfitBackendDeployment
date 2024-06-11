from django.contrib.auth.middleware import AuthenticationMiddleware
# from django.dispatch import user_authenticated  # Assuming your signal definition
from user.signals import user_authenticated
from django.conf import settings
import jwt
from user.models import UserAccount
from django.contrib.auth.models import AnonymousUser
from rest_framework.response import Response
from rest_framework import status

# middleware that triggers a signal and turns the user logged in field to true
class AuthenticationWithSignalMiddleware(AuthenticationMiddleware):

    def process_request(self, request):
        super().process_request(request)

        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and 'Bearer' in auth_header:
            token = auth_header.split(' ')[1]  # Extract the JWT token part
            try:
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = decoded_token.get('user_id')  # Extract user ID from the token payload
                user = UserAccount.objects.get(pk=user_id)  # Retrieve user from the database
                if user and user.is_authenticated:
                    if not user.logged_in:
                        user_authenticated.send(sender=self.__class__, user=user)
            except jwt.ExpiredSignatureError:
                print("Token expired.")
            except jwt.InvalidTokenError:
                print("Invalid token.")
            except UserAccount.DoesNotExist:
                print("User not found.")
        return None


# from django.contrib.auth.middleware import AuthenticationMiddleware
# from django.conf import settings
# import jwt
# from user.models import UserAccount
# from django.http import JsonResponse
# from rest_framework import status
# from user.signals import user_authenticated

# class AuthenticationWithSignalMiddleware(AuthenticationMiddleware):

#     def process_request(self, request):
#         super().process_request(request)

#         auth_header = request.META.get('HTTP_AUTHORIZATION')
#         if auth_header and 'Bearer' in auth_header:
#             token = auth_header.split(' ')[1]  # Extract the JWT token part
#             try:
#                 decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
#                 user_id = decoded_token.get('user_id')  # Extract user ID from the token payload
#                 user = UserAccount.objects.get(pk=user_id)  # Retrieve user from the database
#                 if user and user.is_authenticated:
#                     """If user is blocked by admin the request is stopped from proceeding further"""
#                     if user.blocked:
#                         return JsonResponse({"error": "You have been temporarily blocked by the admin."}, status=status.HTTP_403_FORBIDDEN)
#                     elif not user.logged_in:
#                         user_authenticated.send(sender=self.__class__, user=user)
#                         user.logged_in = True
#                         user.save()
#             except jwt.ExpiredSignatureError:
#                 print("Token expired.")
#             except jwt.InvalidTokenError:
#                 print("Invalid token.")
#             except UserAccount.DoesNotExist:
#                 print("User not found.")
#         return None


                    # print("User extracted from token:", user)
                    # if not user.logged_in:
                    #     user_authenticated.send(sender=self.__class__, user=user)
                    # """If user is blocked by admin the request is stopped from proceeding futher"""
                    # if user.blocked:
                    #     return Response({"error": "You have been temporarily blocked by the admin."}, status=status.HTTP_403_FORBIDDEN)