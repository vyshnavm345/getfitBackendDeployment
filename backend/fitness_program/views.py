from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import FitnessProgram, Lesson, Progress
from .serializers import FitnessProgramSerializer, ProgrammeLessonSerializer, PopularProgramSerializer, PublishRequestSerializer, LessonProgressSerializer
from trainer.models import Trainer_profile
from django.shortcuts import get_object_or_404
from user.permissions.admin_permission import IsAdminUser
from .models import PublishRequest
from user.models import UserAccount

# create new programme
class FitnessProgramCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        # print("The request is :", request.data)
        serializer = FitnessProgramSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':"Programme created"}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# retrive all the available programms
class FitnessProgramListAPIView(APIView):
    def get(self, request): 
        programs = FitnessProgram.objects.filter(is_published=True).order_by('-id')
        serializer = FitnessProgramSerializer(programs, many=True)
        # print("programme list : ", serializer.data[0])
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#admin retrival of the fitness programms
class FitnessProgramList(APIView):
    # only admin can access these methods
    permission_classes = [IsAdminUser]
    def get(self, request):
        programs = FitnessProgram.objects.all().order_by('-id')
        print(programs)
        serializer = FitnessProgramSerializer(programs, many=True)
        print("programme list : ", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# retrive individual programme
class Get_fitness_program(APIView):
    def get(self, request, pk):
        program = FitnessProgram.objects.get(id=pk)
        serializer = FitnessProgramSerializer(program)
        # print("serialized programme data : ", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# retrive programms of individual trainers
class Get_trainer_programme(APIView):
    def get(self, request, pk):
        try:
            trainer = Trainer_profile.objects.get(id=pk)
            # print("The trainer is : ", trainer)
            programs = FitnessProgram.objects.filter(trainer=trainer)
            # print("The programmes are : ", programs)
            serializer = FitnessProgramSerializer(programs ,many=True)
            # print("serialized programme data : ", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message": "sorry cannot retrive the trainer programmes"}, status=status.HTTP_400_BAD_REQUEST)
    
# create new lesson for a programme
class CreateLesson(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        program = FitnessProgram.objects.get(id=pk)
        # print("this is the programme")
        id =request.data.get('id')
        # lesson = Lesson.objects.get(id=id)
        if id:
            # print("The form is for updation ", request.data)
            try:
                message = self.updateLesson(request, id)
                # print("back in the get method")
                return Response(message, status=status.HTTP_200_OK)
            except:
                return Response({"message":"Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = ProgrammeLessonSerializer(data=request.data)
            lesson_no = request.data.get('lesson_number')
            already_exists = Lesson.objects.filter(lesson_number=lesson_no).exists()
            if already_exists:
                return Response({"message": "Lesson number already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                # print("data is valid")
                serializer.save(program=program)
                # print("serializer is saved")
                return Response({'message':"Lesson Added"}, status=status.HTTP_201_CREATED)
            print("serializer error is", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def updateLesson(self, request, id):
        # print("updating the lesson")
        lesson = Lesson.objects.get(id=id)
        data = request.data.copy() 
        if isinstance(request.data.get('image'), str):
            # print("image is a string")
            del data['image']
        serializer = ProgrammeLessonSerializer(instance=lesson, data=data, partial=True)
        # print("the data has been updated")
        if serializer.is_valid():
            # print("Serializer is valid : data ")
            serializer.save()
            message = {'message': "Lesson updated successfully"}
            return message
        #     return Response({'message': "Lesson updated successfully"}, status=status.HTTP_200_OK)
        # print("error: ",serializer.errors)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
        
        
    
# get the list of lessons of particular program
class GetLessonList(APIView):
    def get(self, request, pk):
        try:
            lessons = Lesson.objects.filter(program_id=pk).order_by("lesson_number")
            serializer = ProgrammeLessonSerializer(lessons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message":"Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        

class DeleteLesson(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            lesson = get_object_or_404(Lesson, id=pk)
            lesson.delete()
            return Response({'message': 'Lesson deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Lesson.DoesNotExist:
            return Response({'message': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class GetProgramCount(APIView):
    def get(self, request):
        try:
            # print("Total user called")
            count = FitnessProgram.objects.all().count()
            # print("Total user : ", count)
            return Response({count}, status=status.HTTP_200_OK)
        except Exception as e:
            # print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
        
class GetPopularProgram(APIView):
    def get(self, request):
        try:
            popular_programs = []
            # programs = FitnessProgram.objects.select_related('trainer').all()  # Optimize queries
            programs = FitnessProgram.objects.select_related('trainer').order_by('-followers')
            for program in programs:
                count = program.followers.all().count()
                new = {
                'followers': count,
                'name': program.program_name,
                'sales': count * program.price,
                'trainer': program.trainer.username(),
                }
                # print(new)
                if new not in popular_programs:
                    popular_programs.append(new)
            popular_programs = sorted(popular_programs, key=lambda p: p['followers'], reverse=True)
            # returning the top 5 best sellers
            serializer = PopularProgramSerializer(popular_programs[:5], many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error:", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


# to publish or block a fitness program
class ChangePublishStatus(APIView):
    print("publish status called")
    # only admin can access these methods
    permission_classes = [IsAdminUser]
    def get(self, request, id):
        try:
            program = FitnessProgram.objects.get(id=id)
            
            program.is_published = not program.is_published
            program.save()
            print("program", program)
            print(program.is_published)
            message = "Program Published" if program.is_published else  "Program Blocked"
            print(message)
            
            return Response({"messsage": message}, status=status.HTTP_200_OK)
        except Exception as e:
            print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        

class PublishRequestHandler(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            print("inside function")
            existing_request = PublishRequest.objects.get(id=id)
            if existing_request:
                return Response({"message":"Request already submitted"}, status=status.HTTP_200_OK)

        except PublishRequest.DoesNotExist:  # Handle case where request doesn't exist
            user = request.user
            program = FitnessProgram.objects.get(id=id)
            new_request = PublishRequest.objects.create(sender=user, fitnessProgram=program)

            program.is_published = not program.is_published
            program.save()

            message = "Program Published" if program.is_published else "Program Blocked"

            return Response({"message": message}, status=status.HTTP_200_OK)

        except Exception as e:  # Handle other potential exceptions
            print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

class GetPublishRequests(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        try:
            print("Total get publish request is called")
            pending_requests = []
            new_requests = PublishRequest.objects.filter(approved=False)
            for request in new_requests:
                pending_requests.append(request.fitnessProgram)
            print("The pending requests are",pending_requests)
            # print("Total user : ", count)
            serializer = FitnessProgramSerializer(pending_requests, many=True)
            print("The serialized data is : ", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        

class Publishprogram(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, id):
        try:
            program_to_publish = FitnessProgram.objects.get(id=id)
            program_request = PublishRequest.objects.get(id=id)
            
            program_request.approved = True
            program_request.save()
            
            program_to_publish.is_published = True
            program_to_publish.save()
            
            # print("The pending requests are",pending_requests)
            # print("Total user : ", count)
            # serializer = FitnessProgramSerializer(pending_requests, many=True)
            # print("The serialized data is : ", serializer.data)
            return Response({"message":"Program Published"}, status=status.HTTP_200_OK)
        except Exception as e:
            print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
        
class SavelessonProgress(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, id):
        try:
            print("inside view")
            user = request.user
            #eg: id = "26-1"
            program_id, lesson_id = id.split('-')
            program = FitnessProgram.objects.get(id=int(program_id))
            print("The program : ", program)
            lesson = Lesson.objects.get(lesson_number=id)
            # progress = Progress.objects.create(user=user, program=program, current_lesson=lesson, is_completed=True)
            
            existing_progress = Progress.objects.filter(user=user, program=program, current_lesson=lesson).first()
            print("Existing progress is : ", existing_progress)
            if not existing_progress:
                print("creating the progress")
                progress = Progress.objects.create(user=user, program=program, current_lesson=lesson, is_completed=True)
                return Response({"message": "Lesson marked as completed"}, status=status.HTTP_201_CREATED)
            else:
                print("already created")
                return Response({"message": "Lesson already marked as completed"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        


# class GetlessonProgress(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, user_id, id):
#         try:
#             user = UserAccount.objects.get(id=user_id)
#             program_id, lesson_id = id.split('-')
#             program = FitnessProgram.objects.get(id=int(program_id))
#             data = {
#                 "user": user,
#                 "program": program,
#             }

#             serializer = LessonProgressSerializer(data)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except Exception as e:
#             print("Error:", str(e))
#             return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class GetCompletedlessons(APIView):
    permissions =[permissions.IsAuthenticated]
    
    def get(self, request, id):
        try:
            user = request.user
            program = FitnessProgram.objects.get(id=id)
            print("The program : ", program)
            # progress = Progress.objects.create(user=user, program=program, current_lesson=lesson, is_completed=True)
            
            existing_progress = Progress.objects.filter(user=user, program=program, current_lesson=lesson)

            if not existing_progress:
                progress = Progress.objects.create(user=user, program=program, current_lesson=lesson, is_completed=True)
                return Response({"message": "Lesson completed"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Lesson already marked as completed"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            print("error : ", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class GetlessonProgress(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, id):
        try:
            user = UserAccount.objects.get(id=user_id)
            program_id, lesson_id = id.split('-')
            program = FitnessProgram.objects.get(id=int(program_id))
            data = {
                "user": user,
                "program": program,
            }

            serializer = LessonProgressSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print("Error:", str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)