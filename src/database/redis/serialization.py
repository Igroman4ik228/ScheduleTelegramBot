# ruff: noqa: S301
import pickle
from abc import ABC, abstractmethod
from typing import Any


class AbstractSerializer(ABC):
    @abstractmethod
    def serialize(self, obj: Any) -> Any:
        "Support for serializing objects stored in Redis."
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, obj: Any) -> Any:
        "Support for deserializing objects stored in Redis."
        raise NotImplementedError


class PickleSerializer(AbstractSerializer):
    "Serialize values using pickle."

    def serialize(self, obj: Any) -> bytes:
        return pickle.dumps(obj)

    def deserialize(self, obj: bytes) -> Any:
        "Deserialize values using pickle."
        return pickle.loads(obj)
