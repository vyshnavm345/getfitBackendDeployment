from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

from .models import Profile, FollowedPrograms
from django.contrib.auth import get_user_model
from .models import UserAccount

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password", "profile_picture")

    # validates the password using django inbuilt validators
    def validate(self, data):
        user = User(**data)
        password = data.get("password", user)
        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            # Convert the validation error into serializer errors
            serializer_errors = serializers.as_serializer_error(e)
            raise exceptions.ValidationError(
                {"password": serializer_errors["non_field_errors"]}
            )
        return data

    def create(self, validated_data):
        profile_picture = validated_data.pop("profile_picture", None)
        user = User.objects.create_user(**validated_data)

        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
        print("user created in serializer")
        return user


class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(
        max_length=None, use_url=True, allow_null=True, required=False
    )
    user_id = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "is_staff",
            "user_id",
            "blocked"
        )

    def get_user_id(self, obj):
        if obj:
            return obj.id
        else:
            return None
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["height", "weight", "body_fat", "age", "phone"]


class UserWithProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "is_trainer",
            "is_superuser",
            "profile",
        ]

# class FollowedProgramSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FollowedPrograms
#         fields = '__all__'
        
from fitness_program.serializers import UpdatedFitnessProgramSerializer, FitnessProgramSerializer

class UserFollowedProgramSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    program = FitnessProgramSerializer(many=True, read_only=True)

    class Meta:
        model = FollowedPrograms
        fields = ['id', 'user', 'user_name', 'program', 'status', 'created_on']
        
    def get_user_name(self, obj):
        return obj.user.fullname()


class FollowedProgramSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    program = serializers.SerializerMethodField()

    class Meta:
        model = FollowedPrograms
        fields = ['id', 'user', 'username', 'program', 'status', 'created_on']
        
    def get_username(self, obj):
        return obj.user.fullname()
    
    def get_program(self, obj):
        trainer_id = self.context.get('trainer_id')
        programs = obj.program.filter(trainer__id=trainer_id)
        return UpdatedFitnessProgramSerializer(programs, many=True, context=self.context).data
    
    
