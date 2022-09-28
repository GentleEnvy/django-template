from abc import ABC, abstractmethod
from typing import Type, TypeAlias

from app.base.entities.base import BaseEntity
from app.base.models.base import BaseModel

_EntityType: TypeAlias = Type[BaseEntity] | Type[BaseModel]


class BaseAction(ABC):
    InEntity: Type[_EntityType] = None
    OutEntity: Type[_EntityType] = None

    @abstractmethod
    def run(self, data: 'InEntity') -> 'OutEntity':
        raise NotImplementedError
