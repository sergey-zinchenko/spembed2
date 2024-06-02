from typing import Iterable, Optional
import numpy as np
from injector import inject
from completion_embeddings_provider import CompletionEmbeddingsProvider
from matching_strategy_config import MatchingStrategyConfig
from open_ai_api_wrapper import OpenAiApiWrapper
from package import Package
import logging


class PackageCompletionEmbeddingsProvider(CompletionEmbeddingsProvider[Package]):
    __logger: Optional[logging.Logger]

    @inject
    def __init__(self, wrapper: OpenAiApiWrapper,
                 config: MatchingStrategyConfig,
                 logger: Optional[logging.Logger]) -> None:
        if not config:
            raise ValueError("config is missing or empty")
        if not isinstance(config, MatchingStrategyConfig):
            raise TypeError("config must be an instance of MatchingStrategyConfig")
        if logger and not isinstance(logger, logging.Logger):
            raise TypeError("logger must be an instance of Logger")
        self.__logger = logger
        super().__init__(
            config.package_template,
            wrapper,
            config.batch_size
        )

    async def get_embeddings(self, items: Iterable[Package]) -> np.ndarray:
        if self.__logger:
            self.__logger.info("Getting package completion embeddings")
        try:
            return await super().get_embeddings(items)
        finally:
            if self.__logger:
                self.__logger.debug("Package completion embeddings obtained")
