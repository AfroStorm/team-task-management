from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from api import models, serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserView(ModelViewSet):
    """
    A Modelviewset for the CustomUSer model.
    """

    queryset = User.objects.all()
    serializer_class = serializers.CustomUserSerializer
    authentication_classes = [TokenAuthentication]
