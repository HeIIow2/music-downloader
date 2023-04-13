import logging
from typing import Callable

from .config import SingleAttribute, ListAttribute, StringAttribute, Section

LOG_LEVELS = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0
}


class LoggerAttribute(SingleAttribute):
    @property
    def object_from_value(self) -> logging.Logger:
        return logging.getLogger(self.value)


class LogLevelAttribute(SingleAttribute):
    @property
    def object_from_value(self) -> int:
        """
        gets the numeric value of a log level
        :return:
        """
        if self.value.isnumeric():
            return int(self.value)

        v = self.value.strip().upper()

        if v not in LOG_LEVELS:
            raise ValueError(
                f"{self.name} can only been either one of the following levels, or an integer:\n"
                f"{';'.join(key for key in LOG_LEVELS)}"
            )

        return LOG_LEVELS[v]


class LoggingSection(Section):
    def __init__(self):
        self.FORMAT = StringAttribute(
            name="logging_format",
            description="Reference for the logging formats: https://docs.python.org/3/library/logging.html#logrecord-attributes",
            value=logging.BASIC_FORMAT
        )
        self.LOG_LEVEL = LogLevelAttribute(
            name="log_level",
            description=f"can only been either one of the following levels, or an integer:\n"
                        f"{';'.join(key for key in LOG_LEVELS)}",
            value=str(logging.INFO)
        )

        self.DOWNLOAD_LOGGER = LoggerAttribute(
            name="download_logger",
            description="The logger for downloading.",
            value="download"
        )
        self.TAGGING_LOGGER = LoggerAttribute(
            name="tagging_logger",
            description="The logger for tagging id3 containers.",
            value="tagging"
        )
        self.CODEX_LOGGER = LoggerAttribute(
            name="codex_logger",
            description="The logger for streaming the audio into an uniform codex.",
            value="codex"
        )
        self.OBJECT_LOGGER = LoggerAttribute(
            name="object_logger",
            description="The logger for creating Data-Objects.",
            value="object"
        )
        self.DATABASE_LOGGER = LoggerAttribute(
            name="database_logger",
            description="The logger for Database operations.",
            value="database"
        )
        self.MUSIFY_LOGGER = LoggerAttribute(
            name="musify_logger",
            description="The logger for the musify scraper.",
            value="musify"
        )
        self.YOUTUBE_LOGGER = LoggerAttribute(
            name="youtube_logger",
            description="The logger for the youtube scraper.",
            value="youtube"
        )
        self.ENCYCLOPAEDIA_METALLUM_LOGGER = LoggerAttribute(
            name="metal_archives_logger",
            description="The logger for the metal archives scraper.",
            value="metal_archives"
        )
        self.GENIUS_LOGGER = LoggerAttribute(
            name="genius_logger",
            description="The logger for the genius scraper",
            value="genius"
        )
