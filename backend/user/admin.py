from django.contrib import admin
from .models import UserAccount, Profile, FollowedPrograms

# Register your models here.
admin.site.register(UserAccount)
admin.site.register(Profile)
admin.site.register(FollowedPrograms)
