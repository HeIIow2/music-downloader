from dataclasses import dataclass
from typing import Optional, List, Union

COMMENT_PREFIX = "#"


def comment_string(uncommented: str) -> str:
    unprocessed_lines = uncommented.split("\n")

    processed_lines: List[str] = []

    for line in unprocessed_lines:
        line: str = line.strip()
        if line.startswith(COMMENT_PREFIX) or line == "":
            processed_lines.append(line)
            continue

        line = COMMENT_PREFIX + " " + line
        processed_lines.append(line)

    return "\n".join(processed_lines)


@dataclass
class Attribute:
    name: str
    description: Optional[str]
    value: Union[str, List[str]]

    @property
    def description_as_comment(self):
        return comment_string(self.description)

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
        return self.value.strip()


class IntAttribute(SingleAttribute):
    @property
    def object_from_value(self) -> int:
        if not self.value.isdigit():
            raise ValueError(f"The value of {self.name} needs to be an integer, not {self.value}")

        return int(self.value)


class FloatAttribute(SingleAttribute):
    @property
    def object_from_value(self) -> float:
        if not self.value.isnumeric():
            raise ValueError(f"The value of {self.name} needs to be a number, not {self.value}")

        return float(self.value)


class ListAttribute(Attribute):
    value: List[str]

    def __str__(self):
        return f"{self.description_as_comment}\n" + \
            "\n".join(f"{self.name}={element}" for element in self.value)


@dataclass
class Description:
    description: str

    def __str__(self):
        return comment_string(self.description)


class EmptyLine(Description):
    def __init__(self):
        self.description = ""


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
