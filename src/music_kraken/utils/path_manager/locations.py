from pathlib import Path
import os

import tempfile
from pyffmpeg import FFmpeg

from .music_directory import get_music_directory
from .config_directory import get_config_directory


class Locations:
    def __init__(self, application_name: os.PathLike = "music-kraken"):
        self.FILE_ENCODING: str = "utf-8"
        
        self.TEMP_DIRECTORY = Path(tempfile.gettempdir(), application_name)
        self.TEMP_DIRECTORY.mkdir(exist_ok=True, parents=True)

        self.MUSIC_DIRECTORY = get_music_directory()

        self.CONFIG_DIRECTORY = get_config_directory(str(application_name))
        self.CONFIG_DIRECTORY.mkdir(exist_ok=True, parents=True)
        self.CONFIG_FILE = Path(self.CONFIG_DIRECTORY, f"{application_name}.conf")
        self.LEGACY_CONFIG_FILE = Path(self.CONFIG_DIRECTORY, f"{application_name}.conf")
        
        self.FFMPEG_BIN = Path(FFmpeg(enable_log=False).get_ffmpeg_bin())

    def get_log_file(self, file_name: os.PathLike) -> Path:
        return Path(self.TEMP_DIRECTORY, file_name)
