from typing import Optional
from sqlalchemy import Column, Integer, String, create_engine, Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from matching_strategy_config import MatchingStrategyConfig
from package import Package
from skill import Skill

Base = declarative_base()


class MatchWriter:
    __engine: Engine
    __session_maker: sessionmaker[Session]
    __session: Optional[Session]
    __config: MatchingStrategyConfig

    def __init__(self, output_database: str, config: MatchingStrategyConfig):
        if not output_database:
            raise ValueError("output_database cannot be empty")
        if not isinstance(output_database, str):
            raise TypeError("output_database must be a string")
        if not config:
            raise ValueError("config cannot be empty")
        if not isinstance(config, MatchingStrategyConfig):
            raise TypeError("config must be an instance of MatchingStrategyConfig")
        self.__config = config
        self.__engine = create_engine(output_database)
        self.__session_maker = sessionmaker(bind=self.__engine)
        self.__session = None

    class Match(Base):
        __tablename__ = 'package_to_skill_matches'
        id = Column(Integer, primary_key=True)
        programming_language_name = Column(String)
        package_name = Column(String, nullable=False)
        package_id = Column(Integer, nullable=False)
        skill_name = Column(String, nullable=False)
        skill_id = Column(Integer, nullable=False)

        @staticmethod
        def from_skill_and_package(
                package: Package,
                skill: Skill,
                language: Optional[str] = None) -> 'MatchWriter.Match':
            if language and not isinstance(language, str):
                raise TypeError("language must be a string")
            if not skill:
                raise ValueError("skill is missing or empty")
            if not isinstance(skill, Skill):
                raise TypeError("skill must be an instance of Skill")
            if not package:
                raise ValueError("package is missing or empty")
            if not isinstance(package, Package):
                raise TypeError("package must be an instance of Package")
            return MatchWriter.Match(programming_language_name=language,
                                     package_name=package.label,
                                     package_id=package.key,
                                     skill_name=skill.label,
                                     skill_id=skill.key)

    def __enter__(self):
        if self.__session:
            return self
        Base.metadata.create_all(self.__engine)
        self.__session = self.__session_maker()
        return self

    def __write_matches(self, matches: list[Match]):
        if not matches:
            raise ValueError("matches cannot be empty")
        if not isinstance(matches, list):
            raise TypeError("matches must be a list")
        if not all(isinstance(match, MatchWriter.Match) for match in matches):
            raise TypeError("matches must be a list of MatchWriter.Match")

        self.__session.add_all(matches)

    def write_matches(self, matches: dict[Package, Skill]):
        if not matches:
            raise ValueError("matches cannot be empty")
        if not isinstance(matches, dict):
            raise TypeError("matches must be a dictionary")
        if not all(isinstance(key, Package) for key in matches.keys()):
            raise TypeError("matches keys must be instances of Package")
        if not all(isinstance(value, Skill) for value in matches.values()):
            raise TypeError("matches values must be instances of Skill")
        self.__write_matches([MatchWriter.Match.from_skill_and_package(package, skill,
                                                                       self.__config.programming_language)
                              for package, skill in matches.items()])

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.__session:
            return False
        self.__session.commit()
        self.__session.close()
        self.__session = None
        return False
