from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    message = "You do not have permission to access this resource."

    def has_object_permission(self, request, view, obj):
        return obj.pk == request.user.pk
