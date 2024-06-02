import abc
from typing import TypeVar, Generic, Optional, NamedTuple

from source_item import SourceItem

P1 = TypeVar('P1', bound=SourceItem)
P2 = TypeVar('P2', bound=SourceItem)


class MatchingFilter(Generic[P1, P2], metaclass=abc.ABCMeta):

    class MatchEntry(Generic[P1, P2], NamedTuple):
        terms: P1
        first_match: P2
        first_distance: float
        second_match: P2
        second_distance: float

    @abc.abstractmethod
    async def choose_best_match_for_term(self, matches: list[MatchEntry[P1, P2]]) -> list[Optional[P2]]:
        """Should return the best result between the two given results for the given search term"""
        ...

    @classmethod
    def __subclasshook__(cls, subclass) -> bool:
        return hasattr(subclass, 'choose_best_match_for_term') and callable(subclass.choose_best_match_for_term)
