from ..utils import comment
from .attribute import Attribute

class SingleAttribute(Attribute):
    def __init__(self, name: str, description: str, value: str, pattern: str = None, rule: str = None) -> None:
        super().__init__(name, description, pattern, rule)

        self.string_value = self.input_parse(value)

    @property
    def value(self) -> str:
        return self.output_parse(self.string_value)
    
    @property
    def config_string(self) -> str:
        return  f"{comment(self.description)}\n" \
                f"{self.name}={self.value}\n" \
                f"{comment('RULE: ' + self.rule)}" \
