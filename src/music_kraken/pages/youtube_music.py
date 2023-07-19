from typing import Dict, List, Optional, Set, Type
from urllib.parse import urlparse
import logging
import random
import json
from dataclasses import dataclass
import re

from ..utils.exception.config import SettingValueError
from ..utils.shared import PROXIES_LIST, YOUTUBE_MUSIC_LOGGER
from ..utils.config import CONNECTION_SECTION, write_config

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
    """
    def __init__(self, logger: logging.Logger):
        super().__init__(
            host="https://music.youtube.com/",
            logger=logger,
            hearthbeat_interval=113.25,
        )

        # cookie consent for youtube
        # https://stackoverflow.com/a/66940841/16804841
        self.session.cookies.set(
            name='CONSENT', value='YES+cb.20210328-17-p0.en-GB+FX+{}'.format(random.randint(100, 999)),
            path='/', domain='.youtube.com'
        )
        self.start_hearthbeat()

    def hearthbeat(self):
        r = self.get("https://music.youtube.com/verify_session", is_hearthbeat=True)
        if r is None:
            self.hearthbeat_failed()
        
        string = r.content.decode("utf-8")

        data = json.loads(string[string.index("{"):])
        success: bool = data["success"]

        if not success:
            self.hearthbeat_failed()


@dataclass
class YouTubeMusicCredentials:
    api_key: str

    # ctoken is probably short for continue-token
    # It is probably not strictly necessary, but hey :))
    ctoken: str


class YoutubeMusic(Page):
    # CHANGE
    SOURCE_TYPE = SourcePages.PRESET
    LOGGER = YOUTUBE_MUSIC_LOGGER

    def __init__(self, *args, **kwargs):
        self.connection: YoutubeMusicConnection = YoutubeMusicConnection(logger=self.LOGGER)
        self.credentials: YouTubeMusicCredentials = YouTubeMusicCredentials(
            api_key=CONNECTION_SECTION.YOUTUBE_MUSIC_API_KEY.object_from_value,
            ctoken=""
        )

        if self.credentials.api_key == "":
            self._fetch_from_main_page()
        
        super().__init__(*args, **kwargs)

    def _fetch_from_main_page(self):
        """
        ===API=KEY===
        AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30
        can be found at `view-source:https://music.youtube.com/`
        search for: "innertubeApiKey"
        """
        r = self.connection.get("https://music.youtube.com/")
        if r is None:
            return
        
        content = r.text

        # api key
        api_key_pattern = (
            r"(?<=\"innertubeApiKey\":\")(.*?)(?=\")",
            r"(?<=\"INNERTUBE_API_KEY\":\")(.*?)(?=\")",
        )
        
        api_keys = []
        for api_key_patter in api_key_pattern:
            api_keys.extend(re.findall(api_key_patter, content))
        
        found_a_good_api_key = False
        for api_key in api_keys:
            # save the first api key
            api_key = api_keys[0]
            
            try:
                CONNECTION_SECTION.YOUTUBE_MUSIC_API_KEY.set_value(api_key)
            except SettingValueError:
                continue

            found_a_good_api_key = True
            break

        if found_a_good_api_key:
            write_config()
            self.LOGGER.info(f"Found a valid API-KEY for {type(self).__name__}: \"{api_key}\"")
        else:
            self.LOGGER.error(f"Couldn't find an API-KEY for {type(self).__name__}. :((")


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
