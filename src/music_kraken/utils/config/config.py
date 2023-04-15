from typing import Union, Tuple, Dict, Iterable, List
import logging
import os

from ..path_manager import LOCATIONS
from .base_classes import Description, Attribute, Section, EmptyLine, COMMENT_PREFIX
from .audio import AUDIO_SECTION
from .logging import LOGGING_SECTION


class Config:
    def __init__(self):
        self.config_elements: Tuple[Union[Description, Attribute, Section], ...] = (
            Description("IMPORTANT: If you modify this file, the changes for the actual setting, will be kept as is.\n"
                        "The changes you make to the comments, will be discarded, next time you run music-kraken. "
                        "Have fun!"),
            Description("Those are all Settings for the audio codec.\n"
                        "If you, for some reason wanna fill your drive real quickly, I mean enjoy HIFI music,\n"
                        "feel free to tinker with the Bitrate or smth. :)"),
            AUDIO_SECTION,
            Description("For all your Logging needs.\n"
                        "If you found a bug, and wan't to report it, please set the Logging level to 0,\n"
                        "reproduce the bug, and attach the logfile in the bugreport. ^w^"),
            LOGGING_SECTION,
            Description("🏳️‍⚧️🏳️‍⚧️ Protect trans youth. 🏳️‍⚧️🏳️‍⚧️\n"),
        )

        self._length = 0
        self._section_list: List[Section] = []
        self._name_section_map: Dict[str, Section] = dict()

        for element in self.config_elements:
            if not isinstance(element, Section):
                continue

            self._section_list.append(element)
            for name in element.name_attribute_map:
                if name in self._name_section_map:
                    raise ValueError(f"Two sections have the same name: "
                                     f"{name}: "
                                     f"{element.__class__.__name__} {self._name_section_map[name].__class__.__name__}")

                self._name_section_map[name] = element
                self._length += 1

    def set_name_to_value(self, name: str, value: str):
        if name not in self._name_section_map:
            raise KeyError(f"There is no such setting, as: {name}")

        self._name_section_map[name][name] = value

    def __len__(self):
        return self._length

    @property
    def config_string(self) -> str:
        return "\n\n".join(str(element) for element in self.config_elements)

    def _parse_conf_line(self, line: str, index: int):
        line = line.strip()
        if line.startswith(COMMENT_PREFIX):
            return

        if line == "":
            return

        if "=" not in line:
            raise ValueError(f"Couldn't find the '=' in line {index}.")

        line_segments = line.split("=")
        name = line_segments[0]
        value = "=".join(line_segments[1:])

        self.set_name_to_value(name, value)

    def read_from_config_file(self, path: os.PathLike):
        with open(path, "r") as conf_file:
            for i, line in enumerate(conf_file):
                self._parse_conf_line(line, i+1)

    def write_to_config_file(self, path: os.PathLike):
        with open(path, "w") as conf_file:
            conf_file.write(self.config_string)

    def __iter__(self) -> Iterable[Attribute]:
        for section in self._section_list:
            for name, attribute in section.name_attribute_map.items():
                yield attribute


config = Config()


def read():
    if not LOCATIONS.CONFIG_FILE.is_file():
        write()
    config.read_from_config_file(LOCATIONS.CONFIG_FILE)


def write():
    config.write_to_config_file(LOCATIONS.CONFIG_FILE)
