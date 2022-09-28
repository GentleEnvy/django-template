from __future__ import annotations

from typing import Type

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import exceptions, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import set_rollback

# noinspection PyPackageRequirements
from silk.profiling.profiler import silk_profile

from app.base.authentications.token import TokenAuthentication
from app.base.exceptions import *
from app.base.models.base import BaseModel
from app.base.permissions.base import BasePermission
from app.base.serializers.base import BaseSerializer
from app.base.utils.common import status_by_method
from app.base.utils.schema import extend_schema
from app.users.permissions import IsAuthenticatedPermission

__all__ = ['BaseView']


def _exception_handler(exception):
    try:
        set_rollback()
        if settings.DEBUG and isinstance(exception, MethodNotAllowed):
            return Response(str(exception))
        try:
            raise exception
        except APIWarning as e:
            api_error = e
        except ClientError as e:
            api_error = e
        except CriticalError as e:
            api_error = e
        except tuple(APIWarning.EXCEPTION__CAST.keys()) as exception_to_cast:
            api_error = APIWarning.cast_exception(exception_to_cast)
        except tuple(ClientError.EXCEPTION__CAST.keys()) as exception_to_cast:
            api_error = ClientError.cast_exception(exception_to_cast)
        except tuple(CriticalError.EXCEPTION__CAST.keys()) as exception_to_cast:
            api_error = CriticalError.cast_exception(exception_to_cast)

        error = api_error

    except Exception as e:
        error = CriticalError(str(e))

    error.log()
    return error.to_response()


class BaseView(GenericAPIView):
    lookup_field = 'id'
    ordering = 'id'
    serializer_class = BaseSerializer
    permission_classes = []
    serializer_map: dict[
        str, tuple[int, Type[BaseSerializer]] | Type[BaseSerializer]
    ] = {}
    permissions_map: dict[str, list[Type[BasePermission]]] = {}

    @property
    def method(self) -> str:
        return self.request.method.lower() if hasattr(self, 'request') else ''

    @classmethod
    def _extract_serializer_class_with_status(
        cls, method_name: str
    ) -> tuple[int, Type[BaseSerializer]] | None:
        serializer_class = cls.serializer_map.get(method_name)
        if serializer_class and issubclass(serializer_class, BaseSerializer):
            http_status = status_by_method(method_name)
            return http_status, serializer_class
        return serializer_class

    def get_serializer_class(self) -> Type[BaseSerializer]:
        serializer_class = self._extract_serializer_class_with_status(self.method)
        if serializer_class is None:
            return self.serializer_class
        return serializer_class[1]

    def get_serializer(self, *args, **kwargs) -> BaseSerializer:
        return super().get_serializer(*args, **kwargs)

    def get_valid_serializer(self, *args, **kwargs) -> BaseSerializer:
        kwargs['data'] = self.request.data
        serializer = self.get_serializer(*args, **kwargs)
        serializer.is_valid()
        return serializer

    def get_object(self) -> BaseModel:
        return super().get_object()

    def get_permission_classes(self) -> list[Type[BasePermission]]:
        return self.permission_classes + self.permissions_map.get(self.method, [])

    def get_permissions(self) -> list[BasePermission]:
        return [p() for p in self.get_permission_classes()]

    @classmethod
    def _decorate_methods(cls) -> None:
        def _force_args(f):
            def wrapped_f(*args, **kwargs):
                match f.__code__.co_argcount:
                    case 0:
                        return f()
                    case 1:
                        return f(args[0])
                return f(*args, **kwargs)

            return wrapped_f

        auth_schema = TokenAuthentication.WARNING_401.get_schema()
        for method_name in cls.http_method_names:
            try:
                method = getattr(cls, method_name)
            except AttributeError:
                continue
            responses = {}

            extracted = cls._extract_serializer_class_with_status(method_name)
            if extracted:
                serializer_class = extracted[1]
                if get_schema := getattr(serializer_class, 'get_schema'):
                    responses |= get_schema(extracted[0])

            if IsAuthenticatedPermission in cls.get_permission_classes(cls()):
                responses |= {401: auth_schema}

            method = extend_schema(responses=responses)(method)
            method = _force_args(method)
            setattr(cls, method_name, method)

    @classmethod
    def as_view(cls, **init_kwargs):
        cls._decorate_methods()
        return silk_profile(name='view')(csrf_exempt(super().as_view(**init_kwargs)))

    def handle_exception(self, exception):
        return _exception_handler(exception)

    def permission_denied(self, request, message=None, code=None):
        if request.authenticators and not request.successful_authenticator:
            getattr(request, 'on_auth_fail', lambda: None)()
            raise exceptions.NotAuthenticated()
        raise exceptions.PermissionDenied(detail=message, code=code)

    def list(self):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid()
        serializer.save()
        return Response({'id': serializer.instance.pk}, status=status.HTTP_201_CREATED)

    def retrieve(self):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=self.request.data, partial=True)
        serializer.is_valid()
        serializer.save()

    def destroy(self):
        instance = self.get_object()
        instance.delete()
