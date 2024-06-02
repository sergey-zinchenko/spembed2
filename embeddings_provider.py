import abc
from typing import TypeVar, Generic, Iterable
from source_item import SourceItem

R = TypeVar('R')
P = TypeVar('P', bound=SourceItem)


class EmbeddingsProvider(Generic[P, R], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def get_embeddings(self, items: Iterable[P]) -> R:
        """Embeds the items and returns the embeddings"""
        ...

    @classmethod
    def __subclasshook__(cls, subclass) -> bool:
        return hasattr(subclass, 'get_embeddings') and callable(subclass.get_embeddings) and \
            'return' in subclass.get_embeddings.__annotations__

    @staticmethod
    def raise_when_bad_items(items: Iterable[P]) -> None:
        if not items:
            raise ValueError("items is missing or empty")
        if not isinstance(items, Iterable) or not all(issubclass(item.__class__, SourceItem) for item in items):
            raise TypeError("items must be a Iterable of AISearchableItem")
