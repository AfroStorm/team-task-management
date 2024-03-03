from rest_framework import permissions
from api import models, views


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
                if request.user == obj:
                    return True
