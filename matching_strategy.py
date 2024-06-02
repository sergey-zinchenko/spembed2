from collections.abc import AsyncIterable
from typing import Optional

from injector import inject
from matching_engine import MatchingEngine
from matching_strategy_config import MatchingStrategyConfig
from package import Package
from package_completion_embeddings_provider import PackageCompletionEmbeddingsProvider
from package_to_skill_matching_filter import PackageToSkillMatchingFilter
from raw_embeddings_provider import RawEmbeddingsProvider
from skill import Skill
from skill_completion_embeddings_provider import SkillCompletionEmbeddingsProvider
import logging


class MatchingStrategy:
    __skills_embed_provider: SkillCompletionEmbeddingsProvider
    __packages_embed_provider: PackageCompletionEmbeddingsProvider
    __raw_embed_provider: RawEmbeddingsProvider
    __matching_engine: MatchingEngine[Skill, Package]
    __matching_filter: PackageToSkillMatchingFilter
    __config: MatchingStrategyConfig
    __logger: Optional[logging.Logger]

    @inject
    def __init__(self,
                 skills_embed_provider: SkillCompletionEmbeddingsProvider,
                 packages_embed_provider: PackageCompletionEmbeddingsProvider,
                 raw_embed_provider: RawEmbeddingsProvider,
                 matching_engine: MatchingEngine[Skill, Package],
                 matching_filter: PackageToSkillMatchingFilter,
                 config: MatchingStrategyConfig,
                 logger: Optional[logging.Logger]) -> None:
        if not skills_embed_provider:
            raise ValueError("skills_embed_provider is missing or empty")
        if not isinstance(skills_embed_provider, SkillCompletionEmbeddingsProvider):
            raise TypeError("skills_embed_provider must be an instance of SkillCompletionEmbeddingsProvider")
        if not packages_embed_provider:
            raise ValueError("packages_embed_provider is missing or empty")
        if not isinstance(packages_embed_provider, PackageCompletionEmbeddingsProvider):
            raise TypeError("packages_embed_provider must be an instance of PackageCompletionEmbeddingsProvider")
        if not raw_embed_provider:
            raise ValueError("raw_embed_provider is missing or empty")
        if not isinstance(raw_embed_provider, RawEmbeddingsProvider):
            raise TypeError("raw_embed_provider must be an instance of RawEmbeddingsProvider")
        if not matching_engine:
            raise ValueError("matching_engine is missing or empty")
        if not isinstance(matching_engine, MatchingEngine):
            raise TypeError("matching_engine must be an instance of MatchingEngine")
        if not matching_filter:
            raise ValueError("matching_filter is missing or empty")
        if not isinstance(matching_filter, PackageToSkillMatchingFilter):
            raise TypeError("matching_filter must be an instance of PackageToSkillMatchingFilter")
        if not config:
            raise ValueError("config is missing or empty")
        if not isinstance(config, MatchingStrategyConfig):
            raise TypeError("config must be an instance of MatchingStrategyConfig")
        if logger and not isinstance(logger, logging.Logger):
            raise TypeError("logger must be an instance of Logger")
        self.__skills_embed_provider = skills_embed_provider
        self.__packages_embed_provider = packages_embed_provider
        self.__raw_embed_provider = raw_embed_provider
        self.__matching_engine = matching_engine
        self.__matching_filter = matching_filter
        self.__config = config
        self.__logger = logger

    async def match(self,
                    skills: dict[int, Skill],
                    packages: list[Package]) -> AsyncIterable[dict[Package, Skill]]:
        self.__matching_engine.left_items = skills
        self.__matching_engine.right_items = packages
        i = 0
        while True:
            if self.__logger:
                self.__logger.info(f"Matching iteration {i}")
            left_embed_provider = self.__raw_embed_provider if i == 0 else self.__skills_embed_provider
            right_embed_provider = self.__raw_embed_provider if i == 0 else (
                self.__packages_embed_provider if i % 2 == 0 else None)
            results = await self.__matching_engine.embed_and_search_right_in_left(left_embed_provider,
                                                                                  right_embed_provider,
                                                                                  self.__matching_filter)
            yield results
            if len(results) < self.__config.stop_matching_matches_num:
                break
            i += 1
        if self.__logger:
            self.__logger.info("Matching completed")
