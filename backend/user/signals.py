from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserAccount, Profile


from django.dispatch import Signal

user_authenticated = Signal()

# profile creater
@receiver(post_save, sender=UserAccount)
def create_profile(sender, instance, created, **kwargs):
    print("the user's is_trainer field is ", instance.is_trainer)
    if created:
        if not instance.is_trainer:
            Profile.objects.create(user=instance)
            print("Profile created")


# post_save.connect(create_profile, sender=UserAccount)

# profile updater
@receiver(post_save, sender=UserAccount)
def update_profile(sender, instance, created, **kwargs):
    if created == False:
        instance.profile.save()
        print("Profile Updated!")



# user log in
@receiver(user_authenticated)
def user_authenticated_callback(sender, user, **kwargs):
    print("signal received")
    print("the user is : ", user)
    user.logged_in = True  # Set the logged_in field (assuming it exists in your model)
    user.save()
    print(f"User {user.fullname()} logged in. Status: {user.logged_in}")


# ctrl + shift + l = select dublicates
