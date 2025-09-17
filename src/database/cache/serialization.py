import pickle
from abc import ABC, abstractmethod
from typing import Any


class AbstractSerializer(ABC):
    @abstractmethod
    def serialize(self, obj: Any) -> Any: ...

    @abstractmethod
    def deserialize(self, obj: Any) -> Any: ...


class PickleSerializer(AbstractSerializer):
    def serialize(self, obj: Any) -> bytes:
        return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)

    def deserialize(self, obj: bytes) -> Any:
        return pickle.loads(obj)
