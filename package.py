import csv
from typing import Optional
from source_item import SourceItem


class Package(SourceItem):
    __identity: int
    __title: str
    __description: str

    @property
    def text_to_match(self) -> str:
        return f"{self.__title} {self.__description}"

    @property
    def text_to_filter(self) -> str:
        return self.__title

    @property
    def key(self) -> int:
        return self.__identity

    @property
    def label(self) -> Optional[str]:
        return self.__title

    def __init__(self, identity: int, title: str, description: str) -> None:
        self.__identity = identity
        self.__title = title
        self.__description = description

    @classmethod
    def read_csv(cls, csv_path: str) -> list['Package']:
        if not csv_path:
            raise ValueError("csv_path is missing or empty")
        if not isinstance(csv_path, str):
            raise TypeError("csv_path must be a string")
        with open(csv_path, 'r', encoding='utf-8') as file:
            # noinspection PyTypeChecker
            return [cls(int(row['Id']), row['Title'], row['Description']) for row in csv.DictReader(file) if
                    len(row['Description']) > 40]
