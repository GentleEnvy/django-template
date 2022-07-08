from app.base.permissions.base import BasePermission


class IsAuthenticatedPermission(BasePermission):
    message = 'Вы не авторизованы'

    def _has_permission(self, request, view):
        return getattr(request.user, 'is_authenticated', False)
