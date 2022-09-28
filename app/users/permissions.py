from app.base.permissions.base import BasePermission


class IsAuthenticatedPermission(BasePermission):
    message = "You aren't authenticated"

    def check(self, user):
        return getattr(user, 'is_authenticated', False)

    def _has_permission(self, request, view):
        return self.check(request.user)
