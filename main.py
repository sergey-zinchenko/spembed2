from injector import inject
from match_writer import MatchWriter
from matching_strategy import MatchingStrategy
from matching_strategy_config import MatchingStrategyConfig
from package import Package
from skill import Skill
from utils import Timer


class Main:
    __matching_strategy: MatchingStrategy
    __matching_strategy_config: MatchingStrategyConfig
    __skills: dict[int, Skill]
    __packages: list[Package]
    __match_writer: MatchWriter

    @inject
    def __init__(self, matching_strategy: MatchingStrategy,
                 matching_strategy_config: MatchingStrategyConfig,
                 match_writer: MatchWriter,
                 skills: dict[int, Skill],
                 packages: list[Package]) -> None:
        if not matching_strategy:
            raise ValueError("matching_strategy is missing or empty")
        if not isinstance(matching_strategy, MatchingStrategy):
            raise TypeError("matching_strategy must be an instance of MatchingStrategy")
        if not matching_strategy_config:
            raise ValueError("matching_strategy_config is missing or empty")
        if not isinstance(matching_strategy_config, MatchingStrategyConfig):
            raise TypeError("matching_strategy_config must be an instance of MatchingStrategyConfig")
        if not skills:
            raise ValueError("skills is missing or empty")
        if not isinstance(skills, dict):
            raise TypeError("skills must be a dictionary")
        if not packages:
            raise ValueError("packages is missing or empty")
        if not isinstance(packages, list):
            raise TypeError("packages must be a list")
        if not match_writer:
            raise ValueError("match_writer is missing or empty")
        if not isinstance(match_writer, MatchWriter):
            raise TypeError("match_writer must be an instance of MatchWriter")

        self.__matching_strategy = matching_strategy
        self.__matching_strategy_config = matching_strategy_config
        self.__skills = skills
        self.__packages = packages
        self.__match_writer = match_writer

    async def run(self):
        with Timer() as t:
            async for match_portion in self.__matching_strategy.match(self.__skills, self.__packages):
                with self.__match_writer as writer:
                    writer.write_matches(match_portion)
        print(f"Elapsed time: {float(t):.2f} s")
