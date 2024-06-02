from typing import Optional
import yaml


class MatchingStrategyConfig:
    __stop_matching_matches_num: int
    __min_distance_to_consider: float
    __skill_template: str
    __package_template: str
    __filter_template: str
    __batch_size: int
    __programming_language: Optional[str]

    @property
    def stop_matching_matches_num(self) -> int:
        return self.__stop_matching_matches_num

    @property
    def min_distance_to_consider(self) -> float:
        return self.__min_distance_to_consider

    @property
    def skill_template(self) -> str:
        return self.__skill_template

    @property
    def package_template(self) -> str:
        return self.__package_template

    @property
    def filter_template(self) -> str:
        return self.__filter_template

    @property
    def batch_size(self) -> int:
        return self.__batch_size

    @property
    def programming_language(self) -> Optional[str]:
        return self.__programming_language

    def __init__(self, config: dict) -> None:
        self.__stop_matching_matches_num = config.get('stop_matching_matches_num', 0)
        self.__min_distance_to_consider = config.get('min_distance_to_consider', 0.75)
        self.__skill_template = config.get('skill_template', '')
        self.__package_template = config.get('package_template', '')
        self.__filter_template = config.get('filter_template', '')
        self.__batch_size = config.get('batch_size', 100)
        self.__programming_language = config.get('programming_language', None)

        if (not self.__stop_matching_matches_num or not self.__min_distance_to_consider or not self.__skill_template
                or not self.__package_template or not self.__filter_template or not self.__batch_size):
            raise ValueError("One or more required config fields are missing or empty")
        if self.__min_distance_to_consider < 0.5 or self.__min_distance_to_consider > 0.99:
            raise ValueError("min_distance_to_consider must be between 0.5 and 0.99")

    @classmethod
    def read_config(cls, file_name: str) -> 'MatchingStrategyConfig':
        if not file_name:
            raise ValueError("File name cannot be empty")
        with open(file_name, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return cls(config)
