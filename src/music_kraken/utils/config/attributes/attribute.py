import re

from ...exception.config import SettingValueError
from ..utils import comment


class Description:
    def __init__(self, string: str) -> None:
        self.string = string

    @property
    def config_string(self) -> str:
        return comment(self.string)


class Attribute:
    pattern: str = r'^.*a$'
    rule: str = "This is a default string, it has no rule."
    string_value: str = ""

    def __init__(self, name: str, description: str, pattern: str = None, rule: str = None) -> None:
        if pattern is not None:
            self.pattern = pattern
        if rule is not None:
            self.rule = rule

        self.name = name
        self.description = description

    def validate(self, input_string: str) -> bool:
        return re.match(self.REGEX, input_string) is None
    
    def output_parse(self):
        return self.string_value.strip()

    def input_parse(self, input_string: str) -> str:
        match_result = re.match(self.pattern, input_string)

        if match_result is None:
            raise SettingValueError(
                setting_name=self.name,
                setting_value=input_string,
                rule=self.rule
            )
        
        return match_result.string

    @property
    def value(self) -> str:
        raise NotImplementedError()
    
    @property
    def config_string(self) -> str:
        return NotImplementedError()



attr = Attribute(name="hello world", description="fuck you", value="defaulte")
attr.input_parse("fafda")
attr.input_parse("eeee")
