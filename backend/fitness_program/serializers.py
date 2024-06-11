from rest_framework import serializers
from .models import FitnessProgram, Lesson, PublishRequest, Progress

class FitnessProgramSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    class Meta:
        model = FitnessProgram
        fields = '__all__'
        
    def get_trainer_name(self, obj):
        # print("the returned full name is ", obj.trainer.user.fullname())
        return obj.trainer.user.fullname()
        
class ProgrammeLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        
class PublishRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublishRequest
        fields = '__all__'
        
class UpdatedFitnessProgramSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()

    class Meta:
        model = FitnessProgram
        fields = '__all__'

    def get_trainer_name(self, obj):
        return obj.trainer.user.fullname()

    def to_representation(self, instance):
        request = self.context.get('request')
        if request and hasattr(request, 'trainer_id'):
            # Check if trainer_id is provided in the request
            programs = instance.program.filter(trainer_id=request.trainer_id)
            return super().to_representation(programs)
        else:
            return super().to_representation(instance)
        
class PopularProgramSerializer(serializers.Serializer):
    followers = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    sales = serializers.IntegerField()
    trainer = serializers.CharField(max_length=100)
    
    
class LessonProgressSerializer(serializers.Serializer):
  user = serializers.PrimaryKeyRelatedField(read_only=True)
  program = serializers.PrimaryKeyRelatedField(read_only=True)
  progress_percentage = serializers.SerializerMethodField()

  def get_progress_percentage(self, obj):
    program = obj['program']
    total_lessons = Lesson.objects.filter(program=program).count()
    completed_lessons = Progress.objects.filter(program=program, user=obj['user'], is_completed=True).count()
    if total_lessons > 0 and completed_lessons > 0:
      return (completed_lessons / total_lessons) * 100
    else:
      return 0