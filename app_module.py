from injector import Binder, singleton, multiprovider, Module, provider, noscope

from custom_log_formatter import CustomLogFormatter
from main import Main
from match_writer import MatchWriter
from matching_engine import MatchingEngine
from matching_strategy import MatchingStrategy
from matching_strategy_config import MatchingStrategyConfig
from package_completion_embeddings_provider import PackageCompletionEmbeddingsProvider
from package_to_skill_matching_filter import PackageToSkillMatchingFilter
from skill_completion_embeddings_provider import SkillCompletionEmbeddingsProvider
from open_ai_api_wrapper import OpenAiApiWrapper
from open_ai_api_wrapper_config import OpenAiApiWrapperConfig
from raw_embeddings_provider import RawEmbeddingsProvider
from package import Package
from skill import Skill
import logging


class AppModule(Module):
    __skills_source_path: str
    __packages_source_path: str
    __output_path: str
    __config_path: str
    __log_level: int
    __console_logging_formatter: logging.Formatter = CustomLogFormatter()
    __stream_logging_formatter: logging.Formatter = (
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)'))
    __file_handler: logging.FileHandler = logging.FileHandler('application_module.log')
    __console_handler: logging.StreamHandler = logging.StreamHandler()

    def __init__(self, skills_source_path: str, packages_source_path: str,
                 output_path: str, config_path: str, log_level: int = logging.INFO) -> None:
        if not skills_source_path:
            raise ValueError("skills_source_path is missing or empty")
        if not isinstance(skills_source_path, str):
            raise TypeError("skills_source_path must be a string")
        if not packages_source_path:
            raise ValueError("packages_source_path is missing or empty")
        if not isinstance(packages_source_path, str):
            raise TypeError("packages_source_path must be a string")
        if not output_path:
            raise ValueError("output_path is missing or empty")
        if not isinstance(output_path, str):
            raise TypeError("output_path must be a string")
        if not config_path:
            raise ValueError("config_path is missing or empty")
        if not isinstance(config_path, str):
            raise TypeError("config_path must be a string")
        if not log_level:
            raise ValueError("log_level is missing or empty")
        if not isinstance(log_level, int):
            raise TypeError("log_level must be an integer")
        self.__skills_source_path = skills_source_path
        self.__packages_source_path = packages_source_path
        self.__output_path = output_path
        self.__config_path = config_path
        self.__log_level = log_level
        self.configure_logger()

    def configure_logger(self):
        self.__console_handler.setLevel(self.__log_level)
        self.__console_handler.setFormatter(self.__console_logging_formatter)
        self.__file_handler.setLevel(logging.INFO)
        self.__file_handler.setFormatter(self.__stream_logging_formatter)

    @provider
    def provide_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(self.__log_level)
        logger.addHandler(self.__console_handler)
        logger.addHandler(self.__file_handler)
        return logger

    @multiprovider
    @singleton
    def provide_skills(self) -> dict[int, Skill]:
        return Skill.read_db(self.__skills_source_path)

    @multiprovider
    @singleton
    def provide_packages(self) -> list[Package]:
        return Package.read_csv(self.__packages_source_path)

    @provider
    @singleton
    def provide_match_writer(self, matching_strategy_config: MatchingStrategyConfig) -> MatchWriter:
        return MatchWriter(self.__output_path,
                           matching_strategy_config)

    @provider
    @singleton
    def provide_open_ai_api_wrapper_config(self) -> OpenAiApiWrapperConfig:
        return OpenAiApiWrapperConfig.read_config(self.__config_path)

    @provider
    @singleton
    def provide_matching_strategy_config(self) -> MatchingStrategyConfig:
        return MatchingStrategyConfig.read_config(self.__config_path)

    def configure(self, binder: Binder) -> None:
        binder.bind(OpenAiApiWrapperConfig, to=self.provide_open_ai_api_wrapper_config, scope=singleton)
        binder.bind(OpenAiApiWrapper, to=OpenAiApiWrapper, scope=singleton)
        binder.bind(RawEmbeddingsProvider, to=RawEmbeddingsProvider, scope=singleton)
        binder.bind(PackageCompletionEmbeddingsProvider, to=PackageCompletionEmbeddingsProvider, scope=singleton)
        binder.bind(SkillCompletionEmbeddingsProvider, to=SkillCompletionEmbeddingsProvider, scope=singleton)
        binder.bind(PackageToSkillMatchingFilter, to=PackageToSkillMatchingFilter, scope=singleton)
        binder.bind(MatchingEngine[Skill, Package], to=MatchingEngine, scope=singleton)
        binder.bind(MatchingStrategy, to=MatchingStrategy, scope=singleton)
        binder.bind(MatchingStrategyConfig, to=self.provide_matching_strategy_config, scope=singleton)
        binder.multibind(dict[int, Skill], to=self.provide_skills, scope=singleton)
        binder.multibind(list[Package], to=self.provide_packages, scope=singleton)
        binder.bind(MatchWriter, to=self.provide_match_writer, scope=singleton)
        binder.bind(Main, to=Main, scope=singleton)
        binder.bind(logging.Logger, to=self.provide_logger, scope=noscope)
