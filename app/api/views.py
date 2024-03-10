from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, response, status, permissions as perm, \
    filters, decorators
from rest_framework.authentication import TokenAuthentication
from api import models, serializers, permissions as cust_perm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserView(viewsets.GenericViewSet):
    """
    Manages the CRUD operations for the CustomUser model. The create
    action uses a different serializer to create a CustomUser instance
    together  with its UserProfile.

    Expected fields for update/delete operations:

    - email
    - password
    - password_confirmation

    additional fields for create operation:

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
            permission_classes = [perm.IsAdminUser]

        elif self.action in ['retrieve', 'list']:
            permission_classes = [perm.IsAuthenticated]

        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [cust_perm.IsOwner | perm.IsAdminUser]

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
            serialized_data = self.get_serializer(instance=user).data

            return response.Response(
                {
                    'message': 'User successfully created',
                    'data': serialized_data
                }, status=status.HTTP_201_CREATED
            )

        return response.Response(
            {
                'message': 'Validation error', 'error': serializer.errors

            }, status=status.HTTP_400_BAD_REQUEST

        )

    def update(self, request, pk):
        """
        Updates single CustomUser instances.
        """

        instance = self.get_object()
        serializer = self.get_serializer(
            instance=instance,
            data=request.data
        )
        if serializer.is_valid():
            user = serializer.save()
            serialized_data = self.get_serializer(instance=user).data

            return response.Response(
                {
                    'message': 'User successfully updated',
                    'data': serialized_data
                }, status=status.HTTP_200_OK
            )

        return response.Response(
            {
                'message': 'Validation error', 'error': serializer.errors

            }, status=status.HTTP_400_BAD_REQUEST

        )

    def partial_update(self, request, pk):
        """
        Partially updates single CustomUser instances.
        """

        instance = self.get_object()
        serializer = self.get_serializer(
            instance=instance,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            user = serializer.save()
            serialized_data = self.get_serializer(instance=user).data

            return response.Response(
                {
                    'message': 'User successfully updated',
                    'data': serialized_data
                }, status=status.HTTP_200_OK
            )

        return response.Response(
            {
                'message': 'Validation error', 'error': serializer.errors

            }, status=status.HTTP_400_BAD_REQUEST

        )

    def destroy(self, request, pk):
        """
        Destroys single CustomUser instance.
        """
        instance = self.get_object()
        instance.delete()

        return response.Response(
            {'message': 'User successfully deleted'},
            status.HTTP_204_NO_CONTENT
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


class TaskView(viewsets.ModelViewSet):
    """
    Creates an instance of the CustomUser model with its respective
    UserProfile.

    Expected fields:
    - title
    - description
    - due_date
    - category (Category.name)
    - priority (Priority.caption)
    - status (Status.caption)

    Extra actions:
    - Add team member
    """

    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """
        Returns permission classes based on the acessed view action.
        """

        permission_classes = []
        if self.action in ['add_team_member', 'remove_team_member']:
            permission_classes = [perm.IsAdminUser | cust_perm.IsOwner]

        elif self.action == 'create':
            permission_classes = [perm.IsAdminUser | perm.IsAuthenticated]

        elif self.action in ['partial_update', 'update']:
            permission_classes = [
                perm.IsAdminUser | cust_perm.IsOwner | cust_perm.IsTeamMember
            ]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Saves the request user as the Task owner.
        """
        serializer.validated_data['owner'] = self.request.user.profile
        return super().perform_create(serializer)

    @decorators.action(methods=['patch'], detail=True)
    def add_team_member(self, request, pk):
        """
        Adds a CustomUser to the team_members field of the Task
        instance.

        Allows only:
        - Admin 
        - Task.owner.

        Expected data:
        - {team_members: [request.user.id,]}
        """
        team_members = request.data.get('team_members')
        task_instance = self.get_object()

        def add_team_members(team_members, task_instance):
            """
            Checks if the id within the requet data are valid, then
            retrieves the user(userprofile) instances and adds them
            to the task instance. Sends a bad request response when
            user(userprofile) doesnt exist
            """
            for id in team_members:
                try:
                    team_member = get_object_or_404(User, id=id).profile
                except User.DoesNotExist:
                    return response.Response(
                        {
                            'message': f'''Team member with the id {id}
                            does not exist'''
                        }, status=status.HTTP_400_BAD_REQUEST
                    )

                task_instance.team_members.add(team_member)

        add_team_members(team_members, task_instance)

        serialized_data = self.get_serializer(task_instance).data
        member_list = serialized_data.get('team_members')

        return response.Response(
            {
                'message': 'Team members got successfully added',
                'team_members': member_list
            }, status=status.HTTP_200_OK
        )

    @add_team_member.mapping.delete
    def remove_team_member(self, request, pk):
        """
        Removes a CustomUser from the team_members field of the Task
        instance. Only admin and Task.owner are allowed.

        Expected data:
        - {team_member: id}
        """

        try:
            user_id = request.data.get('team_member')
            team_member = get_object_or_404(User, id=user_id).profile
        except:
            return response.Response(
                {
                    'message': 'Team member does not exist'
                }, status=status.HTTP_400_BAD_REQUEST
            )

        task_instance = self.get_object()
        serialized_data = self.get_serializer(task_instance).data
        member_list = serialized_data.get('team_members')

        if team_member in task_instance.team_members.all():
            task_instance.team_members.remove(team_member)

            serialized_data = self.get_serializer(task_instance).data
            member_list = serialized_data.get('team_members')

            return response.Response(
                {
                    'message': 'Team member got successfully removed',
                    'team_members': member_list
                }, status=status.HTTP_200_OK
            )

        return response.Response(
            {
                'message': 'User is not part of the Tasks team',
                'team_members': member_list
            }, status=status.HTTP_400_BAD_REQUEST
        )
