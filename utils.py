from functools import cached_property
from typing import get_type_hints
import time


def batch_list(items: list[str], batch_size: int) -> list[list[str]]:
    batches_range = range(0, len(items), batch_size)
    return [items[i:i + batch_size] for i in batches_range]


def property_typecheck(cls: object, property_name: str, expected_type: type) -> bool:
    property_obj = getattr(cls, property_name)
    if isinstance(property_obj, cached_property):
        property_obj = property_obj.func
    if isinstance(property_obj, property):
        property_obj = property_obj.fget
    return get_type_hints(property_obj).get('return') == expected_type


class Timer(object):
    def __enter__(self):
        self.t = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.e = time.time()

    def __float__(self):
        return float(self.e - self.t)
