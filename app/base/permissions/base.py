from typing import final

from rest_framework.permissions import BasePermission as _BasePermission


class BasePermission(_BasePermission):
    _allow_super: bool = True
    message: str

    @final
    def has_permission(self, request, view):
        if self._has_permission(request, view):
            return True
        if self._allow_super:
            user = request.user
            if getattr(user, 'is_superuser', False):
                return True
        return False

    def _has_permission(self, request, view):
        return True

    @final
    def has_object_permission(self, request, view, obj):
        if self._has_object_permission(request, view, obj):
            return True
        if self._allow_super:
            user = request.user
            if getattr(user, 'is_superuser', False):
                return True
        return False

    def _has_object_permission(self, request, view, obj):
        return True
