from django.urls import path
from .views import TrainerProfileView, RetriveTrainerProfile, RetriveAllTrainers, GetSubscribers, RetrieveTrainer, GetTrainerContacts, GetTrainerCount, GetLoggedInTrainers, GetAllTrainers

urlpatterns = [
    path("TrainerProfileCreation/", TrainerProfileView.as_view()),
    path("getTrainer/", RetriveTrainerProfile.as_view()),
    path("retrieveTrainer/<int:trainer_id>/", RetrieveTrainer.as_view()),
    path("allTrainer/", RetriveAllTrainers.as_view()),
    path("getTrainerCount/", GetTrainerCount.as_view()),
    path("get_subscribers/", GetSubscribers.as_view()),
    path("getLoggedInTrainers/", GetLoggedInTrainers.as_view()),
    path("getTrainerContacts/", GetTrainerContacts.as_view()),
    path("getAllTrainers/", GetAllTrainers.as_view()),
    
]
