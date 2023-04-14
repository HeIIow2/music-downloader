from dataclasses import dataclass
from typing import Optional, List, Union

COMMENT_PREFIX = "// "


@dataclass
class Attribute:
    name: str
    description: Optional[str]
    value: Union[str, List[str]]

    @property
    def description_as_comment(self):
        lines = self.description.split("\n")

        return "\n".join(f"{COMMENT_PREFIX}{line}" for line in lines)

    @property
    def object_from_value(self):
        return self.value

    def __str__(self):
        return f"{self.description_as_comment}\n{self.name}={self.value}"


class SingleAttribute(Attribute):
    value: str


class StringAttribute(SingleAttribute):
    @property
    def object_from_value(self) -> str:
        return self.value


class ListAttribute(Attribute):
    value: List[str]

    def __str__(self):
        return f"{self.description_as_comment}\n" + \
            "\n".join(f"{self.name}={element}" for element in self.value)


@dataclass
class Description:
    description: str

    def __str__(self):
        return f"\n{self.description}"


class EmptyLine(Description):
    def __init__(self):
        self.description = "\n"


class Section:
    """
    A placeholder class
    """
    attribute_list: List[Union[
        Attribute,
        Description
    ]]

    def __str__(self):
        return "\n".join(attribute.__str__() for attribute in self.attribute_list)
