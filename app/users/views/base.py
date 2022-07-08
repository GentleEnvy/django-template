from app.base.utils.schema import extend_schema
from app.base.views.base import BaseView
from app.users.authentications.token import TokenAuthentication
from app.users.permissions import IsAuthenticatedPermission

__all__ = ['BaseAuthView']


class BaseAuthView(BaseView):
    permission_classes = [IsAuthenticatedPermission]

    @classmethod
    def _to_auth_schema(cls) -> None:
        auth_schema = TokenAuthentication.WARNING_401.to_schema()
        for method_name in cls.http_method_names:
            try:
                method = getattr(cls, method_name)
            except AttributeError:
                continue
            setattr(
                cls, method_name, extend_schema(responses={401: auth_schema})(method)
            )

    @classmethod
    def _to_schema(cls) -> None:
        cls._to_auth_schema()
        super()._to_schema()
