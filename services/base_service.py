"""Abstract base service."""
from typing import Generic, TypeVar
from repositories.base_repository import BaseRepository

T = TypeVar("T")


class BaseService(Generic[T]):
    def __init__(self, repository: BaseRepository[T]):
        self.repository = repository