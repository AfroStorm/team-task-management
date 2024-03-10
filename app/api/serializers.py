from rest_framework import serializers
from rest_framework.validators import ValidationError
from api import models
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
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
    category = serializers.SlugRelatedField(
        queryset=models.Category.objects.all(),
        slug_field='name'
    )

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
    A RUD Serializer for the CustomUser model. expects data for a
    CostumUser and its profile instance.

    fields:
    - email (EmailField)
    - password (CharField)
    - password_confirmation (CharField)
    """
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    password_confirmation = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, attrs):
        """
        Checks if the password and password_confirmation values are
        identical and removes the password_confirmation at the end.
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
        # Removing the password_confirmation
        attrs.pop('password_confirmation', None)

        return super().validate(attrs)

    def update(self, instance, validated_data):
        """
        Custom update method accessing the individual fields within
        the validated_data to update the respective instance
        attributes.
        """

        email = validated_data.get('email', instance.email)
        password = validated_data.get('password', instance.password)

        instance.email = email
        instance.password = password

        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Presents the CustomUser instance as a dictionary with nested 
        dictionries of its foreign key instances.
        """

        # Creates basic user representation data
        desired_fields = [
            'id', 'email', 'is_active', 'is_superuser', 'is_staff'
        ]
        representation = {}
        for field in desired_fields:
            representation[field] = getattr(instance, field)

        profile = getattr(instance, 'profile')
        position = getattr(profile, 'position')

        representation['profile'] = UserProfileSerializer(
            profile
        ).data
        if position:
            representation['profile']['position'] = PositionSerializer(
                profile.position
            ).data
            representation['profile']['position']['category'] \
                = position.category.name

        # Owner = instance.id, removed due redundant
        representation['profile'].pop('owner', None)
        return representation


class UserInitiationSerializer(serializers.Serializer):
    """
    Initiates a CustomUser instance together with its UserProfile.

    Methods:
    - validate
    - to_internal_value
    - create
    - to_representation

    Fields:
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

    def to_internal_value(self, data):
        """
        Restructures the content of the data into 2 nested
        dictionaries (user_data, profile_data) of a new dictionary
        (restructured_data) to prepare the data to be passed into 
        the CustomUser create method, which expects this format.
        """

        data = super().to_internal_value(data)
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

    def to_representation(self, instance):
        """
        Presents the CustomUser instance as a dictionary with nested 
        dictionries of its foreign key instances.
        """

        # Creates basic user representation data
        desired_fields = [
            'id', 'email', 'is_active', 'is_superuser', 'is_staff'
        ]
        representation = {}
        for field in desired_fields:
            representation[field] = getattr(instance, field)

        profile = getattr(instance, 'profile')
        position = getattr(profile, 'position')

        representation['profile'] = UserProfileSerializer(
            profile
        ).data
        if position:
            representation['profile']['position'] = PositionSerializer(
                profile.position
            ).data
            representation['profile']['position']['category'] \
                = position.category.name

        # Owner = instance.id, removed due redundant
        representation['profile'].pop('owner', None)
        return representation


class TaskSerializer(serializers.ModelSerializer):
    """
    A modelserializer for the Task model.
    """

    category = serializers.SlugRelatedField(
        queryset=models.Category.objects.all(),
        slug_field='name'
    )
    priority = serializers.SlugRelatedField(
        queryset=models.Priority.objects.all(),
        slug_field='caption'
    )
    status = serializers.SlugRelatedField(
        queryset=models.Status.objects.all(),
        slug_field='caption'
    )

    class Meta:
        model = models.Task
        fields = '__all__'

    def get_fields(self):
        """
        Only allows staff to modify all fields. Task owner/team_member
        have the following read only fields.

        Read only fields:
        - id (by default)
        - created_at (by default)
        - owner
        - team_members
        - task_resource
        """
        fields = super().get_fields()
        request = self.context.get('request')

        if request and request.user:
            user = request.user
            profile = request.user.profile
            team_members = self.instance.team_members.all()
            owner = self.instance.owner

            if user.is_staff:
                return fields

            elif profile in team_members or profile == owner:
                read_only_fields = ['owner', 'team_members', 'task_resource']
                for field in fields:
                    if field in read_only_fields:
                        fields[field].read_only = True

        return fields

    def to_representation(self, instance):
        """
        Restricts representation for request users that are not a team
        member of the task. Admin users/task owners are exmept from 
        this. Also presents the Task owner and team_members
        (UserProfiles) as the user.email for readability.

        """
        request = self.context.get('request')
        representation = super().to_representation(instance)

        owner_email = instance.owner.owner.email
        team_members = []
        for profile in instance.team_members.all():
            team_member_email = profile.owner.email
            team_members.append(team_member_email)

        # Team members = [profile.id,] -> Team members = [user.email,]
        representation['team_members'] = team_members
        # Owner = profile.id -> Owner = user.email
        representation['owner'] = owner_email

        if request:
            user = request.user
            profile = request.user.profile

            if user.is_staff or profile == instance.owner:
                return representation

            elif profile not in instance.team_members.all():
                return {}

        return representation
