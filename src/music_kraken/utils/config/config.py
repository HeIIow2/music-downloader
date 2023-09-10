from typing import Tuple, Union
from pathlib import Path
import logging

import toml

from .attributes.attribute import Attribute, Description, EmptyLine


class Config:
    def __init__(self, componet_list: Tuple[Union[Attribute, Description, EmptyLine]], config_file: Path) -> None:
        self.config_file: Path = config_file

        self.component_list: Tuple[Union[Attribute, Description, EmptyLine]] = componet_list
        self.loaded_settings: dict = {}

    @property
    def toml_string(self):
        "\n\n".join(component.toml_string for component in self.component_list)

    def write(self):
        with self.config_file.open("w") as conf_file:
            conf_file.write(self.toml_string)

    def read(self):
        if not self.config_file.is_file():
            logging.info(f"Config file at '{self.config_file}' doesn't exist => generating")
            self.write()
            return
        
        toml_data = {}
        with self.config_file.open("r") as conf_file:
            toml_data = toml.load(conf_file)

        for component in self.component_list:
            if isinstance(component, Attribute):
                component.load_toml(toml_data, self.loaded_settings)
