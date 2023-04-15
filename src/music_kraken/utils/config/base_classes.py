import logging
from dataclasses import dataclass
from typing import Optional, List, Union, Dict

from ..exception.config import SettingNotFound, SettingValueError

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

    def validate(self, value: str):
        """
        This function validates a new value without setting it.

        :raise SettingValueError:
        :param value:
        :return:
        """
        pass

    def set_value(self, value: str):
        """
        :raise SettingValueError: if the value is invalid for this setting
        :param value:
        :return:
        """
        self.validate(value)

        self.value = value

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
    def validate(self, value: str):
        if not value.isdigit():
            raise SettingValueError(
                setting_name=self.name,
                setting_value=value,
                rule="has to be a digit (an int)"
            )

    @property
    def object_from_value(self) -> int:
        if not self.value.isdigit():
            return int(self.value)


class BoolAttribute(SingleAttribute):
    def validate(self, value: str):
        if value.lower().strip() not in {"true", "false"}:
            raise SettingValueError(
                setting_name=self.name,
                setting_value=value,
                rule="has to be a bool (true/false)"
            )

    @property
    def object_from_value(self) -> bool:
        return self.value.lower().strip() in {"yes", "y", "t", "true"}


class FloatAttribute(SingleAttribute):
    def validate(self, value: str):
        try:
            float(value)
        except ValueError:
            raise SettingValueError(
                setting_name=self.name,
                setting_value=value,
                rule="has to be numeric (an int or float)"
            )

    @property
    def object_from_value(self) -> float:
        if self.value.isnumeric():
            return float(self.value)


class ListAttribute(Attribute):
    value: List[str]

    has_default_values: bool = True

    def set_value(self, value: str):
        """
        Due to lists being represented as multiple lines with the same key,
        this appends, rather than setting anything.

        :raise SettingValueError:
        :param value:
        :return:
        """
        self.validate(value)

        # resetting the list to an empty list, if this is the first config line to load
        if self.has_default_values:
            self.value = []

        self.value.append(value)

    def __str__(self):
        return f"{self.description_as_comment}\n" + \
            "\n".join(f"{self.name}={element}" for element in self.value)

    def single_object_from_element(self, value: str):
        return value

    @property
    def object_from_value(self) -> list:
        """
        THIS IS NOT THE PROPERTY TO OVERRIDE WHEN INHERETING ListAttribute

        :return:
        """

        parsed = list()
        for raw in self.value:
            parsed.append(self.single_object_from_element(raw))

        return parsed


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

    def __init__(self):
        self.name_attribute_map: Dict[str, Attribute] = dict()
        self.index_values()

    def __str__(self):
        return "\n".join(attribute.__str__() for attribute in self.attribute_list)

    def index_values(self):
        for element in self.attribute_list:
            if not isinstance(element, Attribute):
                continue

            if element.name in self.name_attribute_map:
                raise ValueError(f"Two different Attributes have the same name: "
                                 f"{self.name_attribute_map[element.name]} {element}")

            self.name_attribute_map[element.name] = element

    def modify_setting(self, setting_name: str, new_value: str):
        """
        :raise SettingValueError, SettingNotFound:
        :param setting_name:
        :param new_value:
        :return:
        """

        if setting_name not in self.name_attribute_map:
            raise SettingNotFound(
                setting_name=setting_name
            )

        self.name_attribute_map[setting_name].set_value(new_value)
