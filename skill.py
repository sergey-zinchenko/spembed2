import sqlite3
from typing import Optional
from functools import cached_property
from source_item import SourceItem


class Skill(SourceItem):
    __identifier: int
    __name: str
    __path: str

    @cached_property
    def text_to_match(self) -> str:
        return self.__path.lstrip("\\")

    @cached_property
    def text_to_filter(self) -> str:
        return self.text_to_match

    @cached_property
    def key(self) -> int:
        return self.__identifier

    @cached_property
    def label(self) -> Optional[str]:
        return self.__name

    def __init__(self, identifier: int, name: str, path: str) -> None:
        self.__identifier = identifier
        self.__name = name
        self.__path = path

    @classmethod
    def read_db(cls, db_path: str) -> dict[int, 'Skill']:
        if not db_path:
            raise ValueError("db_path is missing or empty")
        if not isinstance(db_path, str):
            raise TypeError("db_path must be a string")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                  SELECT id as identifier, name, path FROM Skills
                  WHERE path LIKE '%.NET%' OR path LIKE '%C#%'
                   ORDER BY id ASC
                """)
                return {row[0]: cls(*row) for row in cursor.fetchall()}
            finally:
                cursor.close()
