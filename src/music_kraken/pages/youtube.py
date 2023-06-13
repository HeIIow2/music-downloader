from typing import List, Optional, Type
from urllib.parse import urlparse, urlunparse, parse_qs
import logging
from dataclasses import dataclass
from enum import Enum

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
from ..utils.shared import YOUTUBE_LOGGER, INVIDIOUS_INSTANCE


"""
- https://yt.artemislena.eu/api/v1/search?q=Zombiez+-+Topic&page=1&date=none&type=channel&duration=none&sort=relevance
- https://yt.artemislena.eu/api/v1/channels/playlists/UCV0Ntl3lVR7xDXKoCU6uUXA
- https://yt.artemislena.eu/api/v1/playlists/OLAK5uy_kcUBiDv5ATbl-R20OjNaZ5G28XFanQOmM
- https://yt.artemislena.eu/api/v1/videos/SULFl39UjgY
"""


def get_invidious_url(path: str = "", query: str = "", fragment: str = "") -> str:
    _ = ""
    return urlunparse((INVIDIOUS_INSTANCE.scheme, INVIDIOUS_INSTANCE.netloc, path, query, fragment, _))


class YouTubeUrlType(Enum):
    CHANNEL = "channel"
    PLAYLIST = "playlist"
    VIDEO = "watch"
    NONE = ""


class YouTubeUrl:
    """
    Artist
    https://yt.artemislena.eu/channel/UCV0Ntl3lVR7xDXKoCU6uUXA
    https://www.youtube.com/channel/UCV0Ntl3lVR7xDXKoCU6uUXA
    
    Release
    https://yt.artemislena.eu/playlist?list=OLAK5uy_nEg5joAyFjHBPwnS_ADHYtgSqAjFMQKLw
    https://www.youtube.com/playlist?list=OLAK5uy_nEg5joAyFjHBPwnS_ADHYtgSqAjFMQKLw
    
    Track
    https://yt.artemislena.eu/watch?v=SULFl39UjgY&list=OLAK5uy_nEg5joAyFjHBPwnS_ADHYtgSqAjFMQKLw&index=1
    https://www.youtube.com/watch?v=SULFl39UjgY
    """
    
    def __init__(self, url: str) -> None:
        """
        Raises Index exception for wrong url, and value error for not found enum type
        """
        self.id = ""
        parsed = urlparse(url=url)
        
        self.url_type: YouTubeUrlType
        
        type_frag_list = parsed.path.split("/")
        if len(type_frag_list) < 2:
            self.url_type = YouTubeUrlType.NONE
        else:
            try:
                self.url_type = YouTubeUrlType(type_frag_list[1].strip())
            except ValueError:
                self.url_type = YouTubeUrlType.NONE
                
        if self.url_type == YouTubeUrlType.CHANNEL:
            if len(type_frag_list) < 3:
                self.couldnt_find_id(url)
            else:
                self.id = type_frag_list[2]
        
        elif self.url_type == YouTubeUrlType.PLAYLIST:
            query_stuff = parse_qs(parsed.query)
            if "list" not in query_stuff:
                self.couldnt_find_id(url)
            else:
                self.id = query_stuff["list"]
        
        elif self.url_type == YouTubeUrlType.VIDEO:
            query_stuff = parse_qs(parsed.query)
            if "v" not in query_stuff:
                self.couldnt_find_id(url)
            else:
                self.id = query_stuff["v"]
            
        
    def couldnt_find_id(self, url: str):
        YOUTUBE_LOGGER.warning(f"The id is missing: {url}")
        self.url_type = YouTubeUrlType.NONE
        
    @property
    def api(self) -> str:
        if self.url_type == YouTubeUrlType.CHANNEL:
            return get_invidious_url(path=f"/api/v1/channels/playlists/{self.id}")
        
        if self.url_type == YouTubeUrlType.PLAYLIST:
            return get_invidious_url(path=f"/api/v1/playlists/{id}")
        
        if self.url_type == YouTubeUrlType.VIDEO:
            return get_invidious_url(path=f"/api/v1/videos/{self.id}")
        
        return get_invidious_url()
            
    @property
    def normal(self) -> str:
        if self.url_type.CHANNEL:
            return get_invidious_url(path=f"/channel/{self.id}")
        
        if self.url_type.PLAYLIST:
            return get_invidious_url(path="/playlist", query=f"list={self.id}")
        
        if self.url_type.VIDEO:
            return get_invidious_url(path="/watch", query=f"v={self.id}")


class YouTube(Page):
    # CHANGE
    SOURCE_TYPE = SourcePages.YOUTUBE
    LOGGER = YOUTUBE_LOGGER

    def __init__(self, *args, **kwargs):
        self.connection: Connection = Connection(
            host=get_invidious_url(),
            logger=self.LOGGER
        )

        super().__init__(*args, **kwargs)

    def get_source_type(self, source: Source) -> Optional[Type[DatabaseObject]]:
        _url_type = {
            YouTubeUrlType.CHANNEL: Artist,
            YouTubeUrlType.PLAYLIST: Album,
            YouTubeUrlType.VIDEO: Song,
        }
        
        parsed = YouTubeUrl(source.url)
        if parsed.url_type in _url_type:
            return _url_type[parsed.url_type]

    def general_search(self, search_query: str) -> List[DatabaseObject]:
        
        return [Artist(name="works")]

    def label_search(self, label: Label) -> List[Label]:
        return []

    def artist_search(self, artist: Artist) -> List[Artist]:
        # https://yt.artemislena.eu/api/v1/search?q=Zombiez+-+Topic&page=1&date=none&type=channel&duration=none&sort=relevance
        endpoint = get_invidious_url(path="/api/v1/search", query=f"q={artist.name.replace(' ', '+')}+-+Topic&page=1&date=none&type=channel&duration=none&sort=relevance")
        print(endpoint)
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
