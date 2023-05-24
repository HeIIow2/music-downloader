from typing import List, Optional, Type
from urllib.parse import urlparse
import logging


from music_kraken.objects import Source, DatabaseObject
from .abstract import Page
from ..objects import (
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    Label,
)
from ..connection import Connection

class Preset(Page):
    # CHANGE
    SOURCE_TYPE = SourcePages.PRESET
    LOGGER = logging.getLogger("preset")

    def __init__(self):
        self.connection: Connection = Connection(
            host="https://www.preset.cum/",
            logger=self.LOGGER
        )
        
        super().__init__()

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
