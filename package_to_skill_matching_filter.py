import asyncio
from typing import Optional
from injector import inject
from matching_strategy_config import MatchingStrategyConfig
from open_ai_api_wrapper import OpenAiApiWrapper
from package import Package
from matching_filter import MatchingFilter
from skill import Skill
import logging


class PackageToSkillMatchingFilter(MatchingFilter[Package, Skill]):
    __wrapper: OpenAiApiWrapper
    __config: MatchingStrategyConfig
    __logger: Optional[logging.Logger]

    @inject
    def __init__(self, wrapper: OpenAiApiWrapper,
                 config: MatchingStrategyConfig,
                 logger: Optional[logging.Logger]) -> None:
        if not wrapper:
            raise ValueError("wrapper is missing or empty")
        if not isinstance(wrapper, OpenAiApiWrapper):
            raise TypeError("wrapper must be an instance of OpenAiApiWrapper")
        if not config:
            raise ValueError("config is missing or empty")
        if not isinstance(config, MatchingStrategyConfig):
            raise TypeError("config must be an instance of MatchingStrategyConfig")
        if logger and not isinstance(logger, logging.Logger):
            raise TypeError("logger must be an instance of Logger")
        self.__wrapper = wrapper
        self.__config = config
        self.__logger = logger

    def log_match(self, package: Package, skill1: Skill, skill2: Skill, match: Optional[Skill]) -> None:
        if self.__logger:
            self.__logger.info(f"Matched {package.label[:50]:<40} with {skill1.label[:50]:<40} "
                               f"and {skill2.label[:50]:<40} as {match.label[:50] if match else 'None'}")

    async def __choose_best_match_for_term_core(self,
                                                match: MatchingFilter.MatchEntry[Package, Skill]) -> Optional[Skill]:
        if match.first_distance < self.__config.min_distance_to_consider:
            return None
        for _ in range(3):
            try:
                ai_response = await self.__wrapper.complete(self.__config.filter_template,
                                                            [(match.terms.text_to_filter,
                                                              match.first_match.text_to_filter,
                                                              match.second_match.text_to_filter)])
                match int(ai_response[0]):
                    case 0:
                        self.log_match(match.terms, match.first_match, match.second_match, None)
                        return None
                    case 1:
                        self.log_match(match.terms, match.first_match, match.second_match, match.first_match)
                        return match.first_match
                    case 2:
                        self.log_match(match.terms, match.first_match, match.second_match, match.second_match)
                        return match.second_match
            except ValueError:
                pass
        return match.first_match

    async def choose_best_match_for_term(self,
                                         matches: list[MatchingFilter.MatchEntry[Package, Skill]]
                                         ) -> list[Optional[Skill]]:
        filtered_list = [match for match in matches if match.first_distance >= self.__config.min_distance_to_consider]
        if self.__logger:
            self.__logger.info(f"Filtering {len(matches)} matches to {len(filtered_list)}")
        task = [asyncio.create_task(self.__choose_best_match_for_term_core(match))
                for match in filtered_list]
        return list(await asyncio.gather(*task))
