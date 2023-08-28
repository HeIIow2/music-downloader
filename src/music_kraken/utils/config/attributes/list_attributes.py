from typing import List

from .attribute import Attribute
from ..utils import comment


class ListAttribute(Attribute):
    def __init__(self, name: str, description: str, value: List[str], pattern: str = None, rule: str = None) -> None:
        super().__init__(name, description, pattern, rule)

        self.string_value_list = []
        self.set_to_list(value)
    

    def set_to_list(self, input_value_list: List[str]):
        self.string_value_list = []
        for input_value in input_value_list:
            self.string_value_list.append(input_value)

    def append(self, input_value: str):
        self.string_value_list.append(self.input_parse(input_value))

    @property
    def value(self) -> str:
        return [self.output_parse(element) for element in self.string_value_list]

    @property
    def config_string(self) -> str:
        NEWLINE = "\n"
        return  f"[{self.name}.start]" \
                f"{comment(self.description)}\n" \
                f"{NEWLINE.join(self.name+'='+v for v in self.string_value_list)}\n" \
                f"{comment('RULE: ' + self.rule)}\n" \
                f"[{self.name}.end]"
