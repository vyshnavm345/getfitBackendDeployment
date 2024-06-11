from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from fitness_program.models import FitnessProgram


class UserAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        email = email.lower()

        user = self.model(first_name=first_name, last_name=last_name, email=email)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, first_name, last_name, email, password=None):
        user = self.create_user(
            first_name,
            last_name,
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    email = models.EmailField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_trainer = models.BooleanField(default=False)
    profile_picture = models.ImageField(
        upload_to="profile/images", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    logged_in= models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    objects = UserAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email
    
    def fullname(self):
        return f"{self.first_name} {self.last_name}" if self.last_name else self.first_name


class Profile(models.Model):
    user = models.OneToOneField(
        UserAccount,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="profile",
    )
    height = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    body_fat = models.FloatField(blank=True, null=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    online_user_ids = models.JSONField(default=list)

    def __str__(self):
        return self.user.first_name

    
class FollowedPrograms(models.Model):
    program = models.ManyToManyField(FitnessProgram, related_name='followers')
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='followed_programs')
    created_on = models.DateField(default=timezone.now)
    status = models.CharField(max_length=50, default="Active")
        
    def __str__(self):
        program_names = ', '.join(program.program_name for program in self.program.all())
        return f"{self.user.first_name} {self.user.last_name} - Programs: {program_names}"
    
    def items(self):
        followed_programs_list = []
        # logic for retriving the list of followed programms by this instance
        return followed_programs_list
    


# class ProgramFollowers(models.Model):
#   program = models.ForeignKey(FitnessProgram, on_delete=models.CASCADE, related_name='program_followers')
#   user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='followed_fitness_programs')
#   created_on = models.DateField(default=timezone.now)

#   class Meta:
#     unique_together = ('program', 'user')  # Enforce unique user-program combination

#   def __str__(self):
#     return f"{self.user.username} follows program: {self.program.program_name}"
    
    
# class Posts(models.Model):
#     title = models.CharField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


