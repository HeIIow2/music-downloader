from dataclasses import dataclass
from typing import Optional, List, Union


@dataclass
class Attribute:
    name: str
    description: Optional[str]
    value: Union[str, List[str]]

    @property
    def object_from_value(self):
        return self.value


class SingleAttribute(Attribute):
    value: str


class StringAttribute(Attribute):
    @property
    def object_from_value(self) -> str:
        return self.value


class ListAttribute(Attribute):
    value: List[str]


class Section:
    """
    A placeholder class
    """
    pass
