from rest_framework import permissions
from api import models, views


class IsTeamMember(permissions.BasePermission):
    """
    Checks if the request.user is a team member of the Task instance.
    """

    def has_object_permission(self, request, view, obj):
        if request and request.user and request.user.is_authenticated:
            profile = request.user.profile

            return profile in obj.team_members.all()


class IsOwner(permissions.BasePermission):
    """
    Checks if the request.user is the owner of the object.
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks if the request.user is the owner of the object.
        """

        if isinstance(view, views.CustomUserView):
            if request and request.user and request.user.is_authenticated:

                return request.user == obj

        if isinstance(view, views.TaskView):
            if request and request.user and request.user.is_authenticated:
                profile = request.user.profile
                task_owner = obj.owner

                return profile == task_owner
