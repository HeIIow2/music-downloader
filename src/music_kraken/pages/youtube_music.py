from typing import Dict, List, Optional, Set, Type
from urllib.parse import urlparse
import logging
import json

from music_kraken.utils.shared import PROXIES_LIST, YOUTUBE_LOGGER


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

class YoutubeMusicConnection(Connection):
    """
    ===Hearthbeat=timings=for=YOUTUBEMUSIC===
    96.27
    98.16
    100.04
    101.93
    103.82

    --> average delay in between: 1.8875 min
    -->

    ===API=KEY===
    AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30
    can be found at `view-source:https://music.youtube.com/`
    search for: "innertubeApiKey"
    """
    def __init__(self, logger: logging.Logger):
        super().__init__(
            host="https://music.youtube.com/",
            logger=logger,
            hearthbeat=True,
            hearthbeat_interval=113.25
        )

    def hearthbeat(self):
        r = self.get("https://music.youtube.com/verify_session", is_hearthbeat=True)
        if r is None:
            self.hearthbeat_failed()
        
        string = r.content.decode("utf-8")

        data = json.loads(string[string.index("{"):])
        success: bool = data["success"]

        if not success:
            self.hearthbeat_failed()


class YoutubeMusic(Page):
    # CHANGE
    SOURCE_TYPE = SourcePages.PRESET
    LOGGER = YOUTUBE_LOGGER

    def __init__(self, *args, **kwargs):
        self.connection: YoutubeMusicConnection = YoutubeMusicConnection(logger=self.LOGGER)
        
        super().__init__(*args, **kwargs)

    def get_source_type(self, source: Source) -> Optional[Type[DatabaseObject]]:
        return super().get_source_type(source)
    
    def general_search(self, search_query: str) -> List[DatabaseObject]:
        return []
    
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
