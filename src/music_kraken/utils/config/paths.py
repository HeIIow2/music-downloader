from pathlib import Path

from ..path_manager import LOCATIONS
from .base_classes import Section, StringAttribute, ListAttribute


class PathAttribute(StringAttribute):
    @property
    def object_from_value(self) -> Path:
        return Path(self.value.strip())


class PathsSection(Section):
    def __init__(self):
        self.MUSIC_DIRECTORY = PathAttribute(
            name="music_directory",
            description="The directory, all the music will be downloaded to.",
            value=str(LOCATIONS.MUSIC_DIRECTORY)
        )

        self.TEMP_DIRECTORY = PathAttribute(
            name="temp_directory",
            description="All temporary stuff is gonna be dumped in this directory.",
            value=str(LOCATIONS.TEMP_DIRECTORY)
        )

        self.LOG_PATH = PathAttribute(
            name="log_file",
            description="The path to the logging file",
            value=str(LOCATIONS.get_log_file("download_logs.log"))
        )

        self.NOT_A_GENRE_REGEX = ListAttribute(
            name="not_a_genre_regex",
            description="These regular expressions tell music-kraken, which sub-folders of the music-directory\n"
                        "it should ignore, and not count to genres",
            value=[
                r'^\.'  # is hidden/starts with a "."
            ]
        )
        
        self.FFMPEG_BINARY = PathAttribute(
            name="ffmpeg_binary",
            description="Set the path to the ffmpeg binary.",
            value=str(LOCATIONS.FFMPEG_BIN)
        )

        self.attribute_list = [
            self.MUSIC_DIRECTORY,
            self.TEMP_DIRECTORY,
            self.LOG_PATH,
            self.NOT_A_GENRE_REGEX,
            self.FFMPEG_BINARY
        ]

        super().__init__()


PATHS_SECTION = PathsSection()
