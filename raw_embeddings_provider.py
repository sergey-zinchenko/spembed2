from typing import Generic, TypeVar, Iterable, Optional
from injector import inject
import utils
import numpy as np
from matching_strategy_config import MatchingStrategyConfig
from source_item import SourceItem
from embeddings_provider import EmbeddingsProvider
from open_ai_api_wrapper import OpenAiApiWrapper
import logging

P = TypeVar('P', bound=SourceItem)


class RawEmbeddingsProvider(Generic[P], EmbeddingsProvider[P, np.ndarray]):
    __wrapper: OpenAiApiWrapper
    __config: MatchingStrategyConfig
    __logger: Optional[logging.Logger]

    @inject
    def __init__(self,
                 wrapper: OpenAiApiWrapper,
                 config: MatchingStrategyConfig,
                 logger: Optional[logging.Logger]) -> None:
        if not wrapper:
            raise ValueError("wrapper is missing or empty")
        if not isinstance(wrapper, OpenAiApiWrapper):
            raise TypeError("wrapper must be an instance of AIWrapper")
        if not config:
            raise ValueError("config is missing or empty")
        if not isinstance(config, MatchingStrategyConfig):
            raise TypeError("config must be an instance of MatchingStrategyConfig")
        self.__wrapper = wrapper
        self.__config = config
        self.__logger = logger

    async def get_embeddings(self, items: Iterable[P]) -> np.ndarray:
        if self.__logger:
            self.__logger.info("Getting raw embeddings for items")
        try:
            self.raise_when_bad_items(items)
            batches = utils.batch_list(list([item.text_to_match for item in items]), self.__config.batch_size)
            embeddings = None
            for batch in batches:
                result = await self.__wrapper.embed_normalize(batch)
                if embeddings is None:
                    embeddings = result
                else:
                    embeddings = np.concatenate((embeddings, result))
            return embeddings
        finally:
            if self.__logger:
                self.__logger.debug(f"Raw embeddings obtained for {len(embeddings)} items")
