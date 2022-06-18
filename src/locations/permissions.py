from rest_framework import permissions


class IsApprovedUser(permissions.BasePermission):
    message = "User is not yet approved."

    def has_permission(self, request, _):
        return request.user.approved is True


class IsApprovedUserOrReadOnly(permissions.BasePermission):
    message = "User is not yet approved."

    def has_permission(self, request, _):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.approved is True
