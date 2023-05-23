from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Type, Union
from urllib.parse import urlparse

import pycountry
import requests
from bs4 import BeautifulSoup

from .abstract import Page
from ..objects import (
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    ID3Timestamp,
    FormattedText,
    Label,
    Options,
    AlbumType,
    AlbumStatus,
    Target
)
from ..utils import string_processing, shared
from .support_classes.download_result import DownloadResult


class YouTube(Page):
    API_SESSION: requests.Session = requests.Session()
    API_SESSION.headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Connection": "keep-alive",
        "Referer": "https://www.youtube.com/"
    }
    API_SESSION.proxies = shared.proxies
    TIMEOUT = 7
    POST_TIMEOUT = 15
    TRIES = 5
    HOST = "https://www.youtube.com"

    SOURCE_TYPE = SourcePages.YOUTUBE

    LOGGER = shared.YOUTUBE_LOGGER


    @classmethod
    def _raw_search(cls, query: str) -> Options:
        return Options()

    @classmethod
    def plaintext_search(cls, query: str) -> Options:
        search_results = []

        return Options(search_results)

    @classmethod
    def _fetch_artist_from_source(cls, source: Source, stop_at_level: int = 1) -> Artist:
        artist: Artist = Artist(source_list=[source])

        return artist

    @classmethod
    def _fetch_album_from_source(cls, source: Source, stop_at_level: int = 1) -> Album:
        album: Album = Album(source_list=[source])
        return album

    @classmethod
    def _get_type_of_url(cls, url: str) -> Optional[Union[Type[Song], Type[Album], Type[Artist], Type[Label]]]:
        return None

    @classmethod
    def _download_song_to_targets(cls, source: Source, target: Target, desc: str = None) -> DownloadResult:
        return DownloadResult()
