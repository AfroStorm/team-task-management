from django.shortcuts import render
from rest_framework import viewsets, response, status, permissions
from rest_framework.authentication import TokenAuthentication
from api import models, serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserView(viewsets.ViewSet):
    """
    Creates an instance of the CustomUser model with its respective
    UserProfile.

    Expected fields:
    - email
    - password
    - password_confirmation
    - first_name
    - last_name
    - position_instance (Position.title)
    """

    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """
        Returns permission classes based on the acessed view action.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]

    def create(self, request):
        """
        Creates a CustomUser instance together with its UserProfile
        instance.

        fields:
        - email (EmailField)
        - password (CharField)
        - password_confirmation (CharField)
        - first_name (CharField)
        - last_name (CharField)
        - position (SlugRelatedField: slug_field='title')
        """

        serializer = serializers.UserInitiationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            serialized_data = serializers.UserInitiationSerializer(
                instance=user
            ).data

            return response.Response(
                {
                    'message': 'User successfully created', 'data': serialized_data
                }, status=status.HTTP_201_CREATED
            )

        return response.Response(
            {
                'message': 'Validation error', 'error': serializer.errors

            }, status=status.HTTP_400_BAD_REQUEST

        )
