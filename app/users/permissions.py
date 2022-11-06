from app.base.permissions.base import BasePermission


class IsAuthenticatedPermission(BasePermission):
    message = "You aren't authenticated"

    def check(self, *args, **kwargs):
        return getattr(kwargs['user'], 'is_authenticated', False)

    def _has_permission(self, request, view):
        return self.check(user=request.user)
