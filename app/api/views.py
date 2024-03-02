from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, response, status, permissions, filters
from rest_framework.authentication import TokenAuthentication
from api import models, serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserView(viewsets.GenericViewSet):
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
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id', 'email']
    ordering_fields = ['id', 'email']

    def get_permissions(self):
        """
        Returns permission classes based on the acessed view action.
        """
        permission_classes = []
        if self.action == 'create':
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Returns the serializer class based on the view action.
        unlike the other view actions the create action is using an
        UserInitiationSerializer.
        """
        if self.action == 'create':
            return serializers.UserInitiationSerializer

        return serializers.CustomUserSerializer

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

        serializer = self.get_serializer(data=request.data)

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

    def list(self, request):
        """
        Retrieves list of multiple CustomUser instances.
        """
        queryset = self.queryset
        serializer = self.get_serializer(
            instance=queryset,
            many=True
        )

        return response.Response(serializer.data)

    def retrieve(self, request, pk):
        """
        Retrieves  single CustomUser instances.
        """

        instance = self.get_object()
        serializer = self.get_serializer(instance=instance)

        return response.Response(serializer.data)
