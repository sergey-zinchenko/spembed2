from typing import TypeVar, Generic, Optional
import numpy as np
from faiss import IndexIDMap, IndexFlatIP
from injector import inject
from matching_filter import MatchingFilter
from package import Package
from skill import Skill
from source_item import SourceItem
from embeddings_provider import EmbeddingsProvider
import logging

SI = TypeVar('SI', bound=SourceItem)
SNI = TypeVar('SNI', bound=SourceItem)


class MatchingEngine(Generic[SI, SNI]):
    __left_items: Optional[dict[int, SI]] = None
    __right_items: Optional[list[SNI]] = None
    __last_right_embeddings: Optional[np.ndarray] = None
    __logger: Optional[logging.Logger]

    @inject
    def __init__(self, logger: Optional[logging.Logger]) -> None:
        if logger and not isinstance(logger, logging.Logger):
            raise TypeError("logger must be an instance of Logger")
        self.__logger = logger

    @property
    def right_items(self) -> list[SNI]:
        if not self.__right_items:
            raise ValueError("right_items is missing or empty")
        return self.__right_items

    @right_items.setter
    def right_items(self, right_items: list[SNI]) -> None:
        if not right_items:
            raise ValueError("right_items is missing or empty")
        if not isinstance(right_items, list):
            raise TypeError("right_items must be a list")
        if not all(issubclass(item.__class__, SourceItem) for item in right_items):
            raise TypeError("right_items must be a list of SourceItem")
        self.__right_items = right_items
        self.__last_right_embeddings = None

    @property
    def left_items(self) -> dict[int, SI]:
        if not self.__left_items:
            raise ValueError("left_items was not set or is empty")
        return self.__left_items

    @left_items.setter
    def left_items(self, left_items: dict[int, SI]) -> None:
        if not left_items:
            raise ValueError("left_items is missing or empty")
        if not isinstance(left_items, dict):
            raise TypeError("left_items must be a dictionary")
        if not all(isinstance(key, int) for key in left_items.keys()):
            raise TypeError("left_items keys must be integers")
        if not all(issubclass(value.__class__, SourceItem) for value in left_items.values()):
            raise TypeError("left_items values must be instances of SourceItem")
        self.__left_items = left_items

    async def embed_and_search_right_in_left(self,
                                             left_embeddings_provider: EmbeddingsProvider[SNI, np.ndarray],
                                             right_embeddings_provider: Optional[EmbeddingsProvider[SI, np.ndarray]],
                                             matching_filter: Optional[MatchingFilter[SNI, SI]] = None
                                             ) -> dict[SNI, SI]:
        if not (self.__right_items and self.__left_items):
            raise ValueError(
                "right_items and left_items should be set before calling embed_all_and_search_left_in_right")

        if not right_embeddings_provider and (
                self.__last_right_embeddings is None or not self.__last_right_embeddings.any()):
            raise ValueError(
                "You can't call this method without providing right_embeddings_provider for the first time")

        if right_embeddings_provider and not isinstance(right_embeddings_provider, EmbeddingsProvider):
            raise TypeError("right_embeddings_provider must be an instance of EmbeddingsProvider")

        if not left_embeddings_provider:
            raise ValueError("left_embeddings_provider is missing or empty")

        if not isinstance(left_embeddings_provider, EmbeddingsProvider):
            raise TypeError("left_embeddings_provider must be an instance of EmbeddingsProvider")

        if matching_filter and not isinstance(matching_filter, MatchingFilter):
            raise TypeError("search_filter must be an instance of SearchFilter")

        if self.__logger:
            self.__logger.info(f"Getting embeddings and searching {len(self.__right_items)} "
                               f"right items in {len(self.__left_items)} left items")

        left_embeddings = await left_embeddings_provider.get_embeddings(self.__left_items.values())
        right_embeddings = await right_embeddings_provider.get_embeddings(
            self.__right_items) if right_embeddings_provider else self.__last_right_embeddings

        embedding_length = left_embeddings.shape[1]
        index = IndexIDMap(IndexFlatIP(embedding_length))
        # noinspection PyArgumentList
        index.add_with_ids(left_embeddings, np.array(list(self.__left_items.keys()), dtype=np.int64))

        # noinspection PyArgumentList
        dest, idx = index.search(right_embeddings, 2)

        matches = [MatchingFilter.MatchEntry[Package, Skill](terms=self.__right_items[i],
                                                             first_match=self.__left_items[idx[i][0]],
                                                             first_distance=dest[i][0],
                                                             second_match=self.__left_items[idx[i][1]],
                                                             second_distance=dest[i][1]) for i in range(len(dest))]

        best_matches = await matching_filter.choose_best_match_for_term(matches)

        matched_indexes, result = [], {}
        for i in range(len(best_matches)):
            if best_matches[i]:
                matched_indexes.append(i)
                result[self.__right_items[i]] = best_matches[i]
        if self.__logger:
            self.__logger.info(f"Validated {len(matches)} matches")

        self.__right_items = np.delete(self.__right_items, matched_indexes).tolist()
        self.__last_right_embeddings = np.delete(right_embeddings, matched_indexes, axis=0)
        return result
