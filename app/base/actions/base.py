from typing import Any, Callable, Final

from app.base.views import base


class BaseAction:
    def __init__(self, view: 'base.BaseView'):
        self.view: Final[base.BaseView] = view

    @property
    def dto(self) -> Callable[[dict], Any]:
        return lambda **data: data

    def run(self, data):
        return self.view.serializer.instance
