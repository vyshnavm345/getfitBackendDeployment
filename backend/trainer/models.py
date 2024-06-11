from django.db import models
# from user.models import UserAccount

class Trainer_profile(models.Model):
    user = models.OneToOneField(
        "user.UserAccount",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="trainer_profile"
    )
    specalized = models.CharField(
        max_length=50, default="General_fitness"
    )
    phone = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="trainer/images", null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    about = models.CharField(max_length=700, null=True, blank=True)
    certifications = models.CharField(max_length=255, blank=True, null=True)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    
    
    def username(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    # Method to retrieve users who have subscribed to the trainer's programs.
    def get_subscribed_users(self):
        subscribed_users = set()
        # Get all programs owned by the trainer
        trainer_programs = self.fitnessprogram_set.all()
        # Traverse through each program and get the users who have subscribed to it
        for program in trainer_programs:
            subscribed_users |= set(program.followers.all())
        return subscribed_users
    
    def __str__(self):
        if self.user:
            return self.user.first_name if self.user.first_name else "Unknown"
        else:
            return "Trainer Profile (No User)"
    
