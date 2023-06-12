from typing import List, Optional, Type
from urllib.parse import urlparse
import logging

from ..objects import Source, DatabaseObject
from .abstract import Page
from ..objects import (
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    Label,
    Target
)
from ..connection import Connection
from ..utils.support_classes import DownloadResult
from ..utils.shared import YOUTUBE_LOGGER


"""
- https://y.com.sb/api/v1/search?q=Zombiez+-+Topic&page=1&date=none&type=channel&duration=none&sort=relevance
- https://y.com.sb/api/v1/channels/playlists/UCV0Ntl3lVR7xDXKoCU6uUXA
- https://y.com.sb/api/v1/playlists/OLAK5uy_kcUBiDv5ATbl-R20OjNaZ5G28XFanQOmM
"""


class YouTube(Page):
    # CHANGE
    SOURCE_TYPE = SourcePages.YOUTUBE
    LOGGER = YOUTUBE_LOGGER

    def __init__(self, *args, **kwargs):
        self.connection: Connection = Connection(
            host="https://www.preset.cum/",
            logger=self.LOGGER
        )

        super().__init__(*args, **kwargs)

    def get_source_type(self, source: Source) -> Optional[Type[DatabaseObject]]:
        return super().get_source_type(source)

    def general_search(self, search_query: str) -> List[DatabaseObject]:
        return [Artist(name="works")]

    def label_search(self, label: Label) -> List[Label]:
        return []

    def artist_search(self, artist: Artist) -> List[Artist]:
        return []

    def album_search(self, album: Album) -> List[Album]:
        return []

    def song_search(self, song: Song) -> List[Song]:
        return []

    def fetch_song(self, source: Source, stop_at_level: int = 1) -> Song:
        return Song()

    def fetch_album(self, source: Source, stop_at_level: int = 1) -> Album:
        return Album()

    def fetch_artist(self, source: Source, stop_at_level: int = 1) -> Artist:
        return Artist()

    def fetch_label(self, source: Source, stop_at_level: int = 1) -> Label:
        return Label()

    def download_song_to_target(self, source: Source, target: Target, desc: str = None) -> DownloadResult:
        return DownloadResult()
