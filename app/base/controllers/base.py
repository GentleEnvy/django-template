from typing import Any, Callable, Final

from app.base.views import base


class BaseController:
    def __init__(self, view: 'base.BaseView'):
        self.view: Final[base.BaseView] = view
        for service_name, service_class in getattr(self, '__annotations__', {}).items():
            if service_class.__name__.endswith('Service'):
                if (service_args := getattr(self, service_name, None)) is None:
                    setattr(self, service_name, service_class())
                else:
                    setattr(self, service_name, service_class(**service_args))
    
    @property
    def dataclass(self) -> Callable[[dict], Any]:
        return lambda **data: data
    
    def control(self, data):
        return self.view.serializer.instance
