import abc
from typing import Optional
from utils import property_typecheck


class SourceItem(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def text_to_match(self) -> str:
        """String value of the item to be embedded"""
        ...

    @property
    @abc.abstractmethod
    def text_to_filter(self) -> str:
        """String value of the item to be embedded"""
        ...

    @property
    @abc.abstractmethod
    def key(self) -> int:
        """Unique integer key for the item"""
        ...

    @property
    @abc.abstractmethod
    def label(self) -> Optional[str]:
        """Optional string label for the item"""
        ...

    def __hash__(self):
        return hash((self.key, self.label, self.text_to_match, self.text_to_filter))

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.key == other.key
                and self.text_to_match == other.text_to_match
                and self.text_to_filter == other.text_to_filter
                and self.label == other.label)

    @classmethod
    def __subclasshook__(cls, subclass) -> bool:
        return all([
            property_typecheck(subclass, attr, type_)
            for attr, type_ in [('key', int), ('text_to_match', str),
                                ('text_to_filter', str), ('label', Optional[str])]
        ])
