from rest_framework import serializers
from rest_framework.validators import ValidationError
from api import models
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ErrorDetail


User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """
    A modelserializer for the Category model.
    """

    class Meta:
        model = models.Category
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    """
    A modelserializer for the Position model.
    """

    class Meta:
        model = models.Position
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    """
    A modelserializer for the UserProfile model.
    """
    class Meta:
        model = models.UserProfile
        fields = '__all__'


class CustomUserSerializer(serializers.Serializer):
    """
    A Serializer for the CustomUser model. expects data for a
    CostumUser and its profile instance.

    fields:
    - email (EmailField)
    - password (CharField)
    - password_confirmation (CharField)
    - first_name (CharField)
    - last_name (CharField)
    - position (SlugRelatedField: slug_field='title')
    """
    # User data
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    password_confirmation = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    # Profile data
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    position = serializers.SlugRelatedField(
        queryset=models.Position.objects.all(),
        slug_field='title'
    )

    def validate(self, attrs):
        """
        Checks if the password and password_confirmation value are
        identical.
        """
        password = attrs.get('password')
        password_confirmation = attrs.get('password_confirmation')
        if password and password_confirmation and\
                password != password_confirmation:
            raise serializers.ValidationError({
                'non_field_errors': [
                    ErrorDetail("Passwords do not match!", code='invalid')
                ]
            })

        return super().validate(attrs)

    def create(self, validated_data):
        """
        Restructures the content of the validated_data into 2 seperate
        dictionaries within it. This happens to prepare the data to be
        passed into the CustomUser create method, which expects 2
        dictionaries (user_data, profile_data).
        """
        email = validated_data.get('email')
        password = validated_data.get('password')
        hashed_password = make_password(password)
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        position = validated_data.get('position')

        new_user = User.objects.create(
            user_data={'email': email, 'password': hashed_password},
            profile_data={
                'first_name': first_name,
                'last_name': last_name,
                'position': position,
            }
        )

        return new_user

    def update(self, instance, validated_data):
        """
        Custom create method to prepare validated_data for being
        saved in the right format.
        """
        email = validated_data.get('email', instance.email)
        password = validated_data.get('password', instance.password)
        first_name = validated_data.get('first_name', instance.first_name)
        last_name = validated_data.get('last_name', instance.last_name)
        position = validated_data.get('position', instance.position)

        instance.email = email
        instance.password = make_password(password)
        instance.first_name = first_name
        instance.last_name = last_name
        instance.position = position

        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Restructures the representation data to a dictionary of nested
        instances.
        """

        # Creates basic user representation data
        representation = {}
        for field, value in instance.__dict__.items():
            # Removes undesired fields retrieved from the instance
            if not field.startswith('_') and field != 'password':
                representation[field] = value

        # Serializes nested instances.
        profile = getattr(instance, 'profile', None)
        if profile:
            profile_data = UserProfileSerializer(profile).data
            representation['profile'] = profile_data

            position = getattr(profile, 'position', None)
            if position:
                position_data = PositionSerializer(position).data
                representation['profile']['position'] = position_data

                category = getattr(position, 'category', None)
                if category:
                    category_data = CategorySerializer(category).data
                    representation['profile']['position']['category'] = category_data

        return representation
