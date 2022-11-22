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
        if pk := view.kwargs.get("pk"):
            location = view.queryset.get(pk=pk)
            return location.community.admin_users.filter(pk=request.user.id).exists()

        return False

    def has_object_permission(self, request, _, obj):
        return obj.community.admin_users.filter(pk=request.user.id).exists()


class IsApprovedUser(permissions.BasePermission):
    message = "User is not yet approved."

    def has_permission(self, request, _):
        if hasattr(request.user, "approved"):
            return request.user.approved is True
        return False
