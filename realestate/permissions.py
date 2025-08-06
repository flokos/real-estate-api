from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows read-only access to authenticated users, but write access only to admins.
    """
    def has_permission(self, request, view):
        # SAFE_METHODS = GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff

class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Read for everyone.
    Write only for owners of the object or admins.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and (
                request.user.is_staff or
                obj == request.user or  # if obj is a User instance
                getattr(obj, "user", None) == request.user  # if obj has a .user field
        )