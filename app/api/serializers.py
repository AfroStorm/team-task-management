from rest_framework import serializers
from rest_framework.validators import ValidationError
from api import models
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ErrorDetail
from collections import OrderedDict


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

    def to_internal_value(self, data):
        """
        Restructures the content of the data into 2 nested
        dictionaries (user_data, profile_data) of a new dictionary
        (restructured_data) to prepare the data to be passed into 
        the CustomUser create method, which expects this format.
        """

        user_fields = ['email', 'password', 'password_confirmation']
        profile_fields = ['first_name', 'last_name', 'position']
        user_data = {}
        profile_data = {}
        restructured_data = OrderedDict()
        for field in data:

            if field in user_fields:
                user_data[field] = data.get(field)
            elif field in profile_fields:
                profile_data[field] = data.get(field)

        restructured_data['user_data'] = user_data
        restructured_data['profile_data'] = profile_data

        return restructured_data

    def validate(self, attrs):
        """
        Checks if the password and password_confirmation values are
        identical and removes the password_confirmation at the end.
        """

        user_data = attrs.get('user_data')

        password = user_data.get('password')
        password_confirmation = user_data.get('password_confirmation')

        if password and password_confirmation and\
                password != password_confirmation:
            raise serializers.ValidationError({
                'non_field_errors': [
                    ErrorDetail("Passwords do not match!", code='invalid')
                ]
            })
        # Removing the password_confirmation
        attrs['user_data'].pop('password_confirmation', None)

        return super().validate(attrs)

    def create(self, validated_data):
        """
        Passing in the restructured validated_data to the
        CostumUserCreate method.
        """
        user_data = validated_data.get('user_data')
        profile_data = validated_data.get('profile_data')

        new_user = User.objects.create(
            user_data=user_data,
            profile_data=profile_data
        )

        return new_user

    def update(self, instance, validated_data):
        """
        Custom update method accessing the individual fields within
        the restructured data to update the respective instance 
        attributes.
        """

        user_data = validated_data.get('user_data')
        profile_data = validated_data.get('profile_data')

        email = user_data.get('email', instance.email)
        password = user_data.get('password', instance.password)

        profile = instance.profile
        first_name = profile_data.get('first_name', profile.first_name)
        last_name = profile_data.get('last_name', profile.last_name)
        position = profile_data.get('position', profile.position)

        instance.email = email
        instance.password = make_password(password)
        profile.first_name = first_name
        profile.last_name = last_name
        profile.position = position

        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Presents the data as a dictionary of nested instances.
        """

        # Creates basic user representation data
        desired_fields = ['id', 'email', 'last_login', 'is_active', 'profile']
        representation = {}
        for field, value in instance.__dict__.items():
            if field in desired_fields:
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
