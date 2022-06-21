from rest_framework import permissions

from locations.models import Community


class ReadOnly(permissions.BasePermission):
    message = "User can only do read-only operations."

    def has_permission(self, request, _):
        return request.method in permissions.SAFE_METHODS


class IsCommunityAdmin(permissions.BasePermission):
    message = "User is not community admin."

    def has_permission(self, request, view):
        if community_pk := view.request.data.get("community"):
            community = Community.objects.get(pk=community_pk)
            return community.admin_users.contains(request.user)
        return False

    def has_object_permission(self, request, _, obj):
        return obj.community.admin_users.contains(request.user)


class IsApprovedUser(permissions.BasePermission):
    message = "User is not yet approved."

    def has_permission(self, request, _):
        if hasattr(request.user, "approved"):
            return request.user.approved is True
        return False
