from typing import TypedDict, List

from urllib.parse import ParseResult
from logging import Logger
from pathlib import Path

from .sections.paths import LOCATIONS
from .config import Config
from .base_classes import Section, Attribute


class SettingsStructure(TypedDict):
    hasnt_yet_started: bool
    result_history: bool
    history_length: int
    happy_messages: List[str]
    modify_gc: bool
    id_bits: int

    # audio
    bitrate: int
    audio_format: str
    sort_by_date: bool
    sort_album_by_type: bool
    download_path: str
    download_file: str
    album_type_blacklist: List[str]

    # connection
    proxies: List[str]
    tor: bool
    tor_port: int
    chunk_size: int
    show_download_errors_threshold: float

    # youtube
    invidious_instance: ParseResult
    piped_instance: ParseResult
    sleep_after_youtube_403: float
    youtube_music_api_key: str
    youtube_music_clean_data: bool
    youtube_url: List[ParseResult]
    use_sponsor_block: bool

    # logging
    logging_format: str
    log_level: int
    download_logger: Logger
    tagging_logger: Logger
    codex_logger: Logger
    object_logger: Logger
    database_logger: Logger
    musify_logger: Logger
    youtube_logger: Logger
    youtube_music_logger: Logger
    metal_archives_logger: Logger
    genius_logger: Logger

    # paths
    music_directory: Path
    temp_directory: Path
    log_file: Path
    not_a_genre_regex: List[str]
    ffmpeg_binary: Path


settings: SettingsStructure = {}


config = Config()
set_name_to_value = config.set_name_to_value


def read_config():
    if not LOCATIONS.CONFIG_FILE.is_file():
        write_config()
    config.read_from_config_file(LOCATIONS.CONFIG_FILE)


def write_config():
    config.write_to_config_file(LOCATIONS.CONFIG_FILE)


def load():
    read_config()

    for section in config.config_elements:
        if not isinstance(section, Section):
            continue

        for attribute in section.attribute_list:
            if not isinstance(attribute, Attribute):
                continue

            settings[attribute.name] = attribute.object_from_value
