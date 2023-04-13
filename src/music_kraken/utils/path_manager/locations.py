from pathlib import Path
import os

import tempfile

from .music_directory import get_music_directory


class Locations:
    def __init__(self, temp_folder_name: os.PathLike = "music-downloader"):
        self.TEMP_DIRECTORY = Path(tempfile.gettempdir(), temp_folder_name)
        self.TEMP_DIRECTORY.mkdir(exist_ok=True)

        self.MUSIC_DIRECTORY = get_music_directory()

    def get_log_file(self, file_name: os.PathLike) -> Path:
        return Path(self.TEMP_DIRECTORY, file_name)
