from django.urls import path
from .views import (
    RegisterView,
    RetriveUserView,
    Retrive_full_user_data,
    update_user_profile,
    Verify_email,
    GetFollowedPrograms,
    GetUserById,
    FollowProgram,
    UnfollowProgram,
    GetUserTrainers,
    GetUserContacts, 
    UserLogout,
    GetUserCount,
    GetLoggedInUsers,
    GetAllUsers,
    ChangeUserAccess,
    # HealthCheck
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("email_verification/", Verify_email.as_view(), name="email_verification"),
    path("me/", Retrive_full_user_data.as_view()),
    path("updateUser/", update_user_profile),
    path("getFollowedPrograms/", GetFollowedPrograms.as_view()),
    path("getUserById/<int:id>/", GetUserById.as_view()),
    path("followProgram/<int:id>/", FollowProgram.as_view()),
    path("unfollowProgram/<int:id>/", UnfollowProgram.as_view()),
    path("getUserTrainers/", GetUserTrainers.as_view()),
    path("getUserContact/", GetUserContacts.as_view()),
    path("getUserCount/", GetUserCount.as_view()),
    path("getLoggedInUsers/", GetLoggedInUsers.as_view()),
    path("getAllUsers/", GetAllUsers.as_view()),
    path("changeUserAccess/<int:id>/", ChangeUserAccess.as_view()),
    path("logout/", UserLogout.as_view()),
    
]
