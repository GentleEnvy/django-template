from abc import ABC, abstractmethod

from app.base.entities.base import BaseEntity
from app.base.models.base import BaseModel

_TypeEntityType = type[BaseEntity | BaseModel]


class BaseAction(ABC):
    InEntity: _TypeEntityType = None  # type:ignore
    OutEntity: _TypeEntityType = None  # type:ignore

    @abstractmethod
    def run(self, data: 'InEntity') -> 'OutEntity':  # type:ignore
        raise NotImplementedError
