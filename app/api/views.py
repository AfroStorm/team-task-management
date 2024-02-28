from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.authentication import TokenAuthentication
from api import models, serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreateView(CreateAPIView):
    """
    Creates an instance of the CustomUser model with its respective
    UserProfile.

    Expected fields:
    - email
    - password
    - password_confirmation
    - first_name
    - last_name
    - position (Position.title)
    """

    serializer_class = serializers.CustomUserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = []

    def create(self, request, *args, **kwargs):

        response = super().create(request, *args, **kwargs)
