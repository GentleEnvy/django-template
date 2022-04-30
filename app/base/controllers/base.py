from typing import Any, Callable

from app.base.views import base


class BaseController:
    def __init__(self, view: 'base.BaseView'):
        self.view = view
        for service_name, service_class in getattr(self, '__annotations__', {}).items():
            if not hasattr(self, service_name):
                setattr(self, service_name, service_class())
    
    @property
    def dataclass(self) -> Callable[[dict], Any]:
        return lambda data: data
    
    def control(self, data) -> dict[str, Any]:
        return self.view.serializer.data
