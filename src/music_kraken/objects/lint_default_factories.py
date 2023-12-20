from typing import List, TypeVar, Type

from .country import Language
from .lyrics import Lyrics
from .parents import OuterProxy
from .song import Song, Album, Artist, Label
from .source import Source
from .target import Target

T = TypeVar('T', bound=OuterProxy)
ALL_CLASSES: List[Type[T]] = [Song, Album, Artist, Label, Source, Target, Lyrics]


def print_lint_res(missing_values: dict):
    print("_default_factories = {")
    for key, value in missing_values.items():
        print(f'\t"{key}": {value},')
    print("}")


def lint_type(cls: T):
    missing_values: dict = {}

    for key, value in cls.__dict__["__annotations__"].items():
        if value is None:
            continue

        if (not key.islower()) or key.startswith("_") or (key.startswith("__") and key.endswith("__")):
            continue

        if key in cls._default_factories:
            continue

        factory = "lambda: None"
        if isinstance(value, str):
            if value == "SourceCollection":
                factory = "SourceCollection"
            elif "collection" in value.lower():
                factory = "Collection"
            elif value.istitle():
                factory = value
        else:
            if value is Language:
                factory = 'Language.by_alpha_2("en")'
            else:
                try:
                    value()
                    factory = value.__name__
                except TypeError:
                    pass

        missing_values[key] = factory

    if len(missing_values) > 0:
        print(f"{cls.__name__}:")
        print_lint_res(missing_values)
        print()
    else:
        print(f"Everything is fine at {cls.__name__}")


def lint():
    for i in ALL_CLASSES:
        lint_type(i)

    print()
