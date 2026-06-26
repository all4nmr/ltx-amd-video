from typing import Protocol, TypeVar
from helpers import device, sync_device, cleanup_memory

ModelType = TypeVar("ModelType")


class ModelConfigurator(Protocol[ModelType]):
    """Protocol for model loader classes that instantiates models from a configuration dictionary."""

    @classmethod
    def from_config(cls, config: dict) -> ModelType: ...
