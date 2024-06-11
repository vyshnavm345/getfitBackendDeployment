from rest_framework import serializers
from .models import Trainer_profile

class TrainerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainer_profile
        fields = ["specalized", "phone", "country", "about", "certifications", "experience_years", "profile_picture"]

# class TrainerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Trainer_profile
#         fields = "__all__"


class TrainerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Trainer_profile
        fields = "__all__"

    def get_username(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        else:
            return "Unknown"
        
    def get_user_id(self, obj):
        if obj.user:
            return obj.user.id
        else:
            return None