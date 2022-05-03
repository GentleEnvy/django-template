from copy import copy
from importlib import import_module

from django.apps import AppConfig


class _BaseAppMeta(type(AppConfig)):
    def __init__(self: type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.__base__ != AppConfig:
            self.default = True


class BaseApp(AppConfig, metaclass=_BaseAppMeta):
    default_auto_field = 'django.db.models.BigAutoField'
    default = False
    
    @property
    def name(self) -> str:
        raise NotImplementedError
    
    def ready(self):
        module_name = self.module.__name__
        views = import_module(f'{module_name}.views')
        for view_name, view in filter(
            lambda item: not item[0].startswith('__') and item[0].endswith('View'),
            views.__dict__.items()
        ):
            name = view_name[:-4]
            view_module_name = view.__module__
            if view_module_name.startswith(module_name):
                path = view_module_name[len(module_name) + 7:]
                for component in ['serializer', 'controller']:
                    view_component_map = copy(getattr(view, f'{component}_map'))
                    for k, v in self._import_components(component, path, name).items():
                        view_component_map.setdefault(k, v)
                    setattr(view, f'{component}_map', view_component_map)
    
    def _import_components(self, component, path, name):
        try:
            components = import_module(f'{self.module.__name__}.{component}s.{path}')
        except ModuleNotFoundError:
            return {}
        component_map = {}
        for component_name, component_class in filter(
            lambda item: not item[0].startswith('__') and item[0].endswith(
                component.capitalize()
            ), components.__dict__.items()
        ):
            method = component_name.split('_')[0].lower()
            if component_name[len(method) + 1:-10] == name:
                component_map[method] = component_class
        return component_map
