from django.urls import path
from .views import FitnessProgramCreateView, FitnessProgramListAPIView, Get_fitness_program, Get_trainer_programme, CreateLesson, GetLessonList, DeleteLesson,  GetProgramCount, GetPopularProgram, ChangePublishStatus, FitnessProgramList, PublishRequestHandler, GetPublishRequests, Publishprogram, SavelessonProgress, GetlessonProgress

urlpatterns = [
    path("create/", FitnessProgramCreateView.as_view()),
    path("retrive_all/", FitnessProgramListAPIView.as_view()),
    path("get_programme/<int:pk>/", Get_fitness_program.as_view()),
    path("get_trainer_programme/<int:pk>/", Get_trainer_programme.as_view()),
    path("createLesson/<int:pk>/", CreateLesson.as_view()),
    path("getLessons/<int:pk>/", GetLessonList.as_view()),
    path("DeleteLesson/<int:pk>/", DeleteLesson.as_view()),
    path("getProgramCount/", GetProgramCount.as_view()),
    path("getPopularProgram/", GetPopularProgram.as_view()),
    path("changePublishStatus/<int:id>/", ChangePublishStatus.as_view()),
    path("retrive_all_programs/", FitnessProgramList.as_view()),
    path("publishRequest/<int:id>/", PublishRequestHandler.as_view()),
    path("getPublishRequests/", GetPublishRequests.as_view()),
    path("publishprogram/<int:id>/", Publishprogram.as_view()),
    path("updatelessonProgress/<str:id>/", SavelessonProgress.as_view()),
    path("getlessonProgress/<int:user_id>/<str:id>/", GetlessonProgress.as_view()),
   
]




