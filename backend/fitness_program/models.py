from django.db import models
from django.utils import timezone
from trainer.models import Trainer_profile
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from urllib.parse import urlparse
# from user.models import UserAccount
def validate_youtube_url(value):
    """
    Custom validator to ensure that the URL belongs to YouTube.
    """
    url_validator = URLValidator()
    try:
        url_validator(value)
    except ValidationError:
        raise ValidationError("Invalid URL")

    parsed_url = urlparse(value)
    if parsed_url.hostname != 'www.youtube.com' and parsed_url.hostname != 'youtube.com':
        raise ValidationError("URL must be from YouTube")

class FitnessProgram(models.Model):
    PROGRAM_CATEGORIES = [
        ("Cardio", "Cardio"),
        ("Weight Loss", "Weight Loss"),
        ("Strength Training", "Strength Training"),
        ("Yoga", "Yoga"),
        ("Pilates", "Pilates"),
        ("HIIT", "HIIT"),
        ("CrossFit", "CrossFit"),
        ("Other", "Other"),
    ]
    
    LEVEL_CHOICES = [
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advance", "Advance"),
    ]
    
    
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, default="Beginner")
    program_name = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in days")
    trainer = models.ForeignKey(Trainer_profile, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)
    cover_image = models.ImageField(upload_to="fitness_programs/images", null=True, blank=True)
    category = models.CharField(max_length=50, choices=PROGRAM_CATEGORIES, default="Other")
    price = models.PositiveIntegerField()
    is_published = models.BooleanField(default=False)
    def __str__(self):
        return self.program_name
    
class Lesson(models.Model):
    title = models.CharField(max_length=255)
    lesson_number=models.CharField(unique=True)
    image = models.ImageField(upload_to="fitness_programs/lessons", null=True, blank=True)
    description = models.TextField()
    video_url = models.URLField(validators=[validate_youtube_url])
    program = models.ForeignKey(FitnessProgram, on_delete=models.CASCADE, related_name='lesson', blank=True, null=True, )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    

class Progress(models.Model):
    user = models.ForeignKey('user.UserAccount', on_delete=models.CASCADE)
    program = models.ForeignKey(FitnessProgram, on_delete=models.CASCADE)
    current_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)    
    # status = models.CharField(max_length=50, default="Completed")
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.first_name} completed lesson {self.current_lesson.lesson_number} of program {self.program.program_name}"
    
    
class PublishRequest(models.Model):
    sender = models.ForeignKey('user.UserAccount', on_delete=models.CASCADE)
    fitnessProgram = models.ForeignObject(FitnessProgram, on_delete=models.CASCADE, from_fields=['id'], to_fields=['id'])
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.sender.first_name} send a request to publish {self.fitnessProgram.program_name}"