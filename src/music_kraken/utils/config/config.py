from typing import Union, Tuple
import logging
import os

from ..path_manager import LOCATIONS
from .base_classes import Description, Attribute, Section, EmptyLine
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
            Description("🏳️‍⚧️🏳️‍⚧️ Protect trans youth. 🏳️‍⚧️🏳️‍⚧️"),
            EmptyLine()
        )

    @property
    def config_string(self) -> str:
        return "\n\n".join(str(element) for element in self.config_elements)

    def write_to_config_file(self, path: os.PathLike):
        with open(path, "w") as conf_file:
            conf_file.write(self.config_string)


config = Config()


def read():
    pass


def write():
    config.write_to_config_file(LOCATIONS.CONFIG_FILE)
