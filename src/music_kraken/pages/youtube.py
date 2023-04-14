from typing import List
import requests
from bs4 import BeautifulSoup
import pycountry

from ..utils.shared import (
    ENCYCLOPAEDIA_METALLUM_LOGGER as LOGGER
)

from .abstract import Page
from ..database import (
    MusicObject,
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    ID3Timestamp,
    FormattedText
)
from ..utils import (
    string_processing
)

INVIDIOUS_INSTANCE = "https://yt.artemislena.eu/api"
"""
NOTE: Implement a switch for different instances, 
Current one is a wacky solution and needs to be changed for
all usecases.
"""

class Youtube(Page):
    """
    This is an abstract class for YouTube downloader.

    To find an artist filter for chanel and search for
    `{artist.name} - Topic`
    and then checks for viable results.

    Ofc you can also implement searching songs by isrc.

    NOTE: I didn't look at the invidious api yet. If it sucks,
    feel free to use projects like youtube-dl.
    But don't implement you're own youtube client.
    I don't wanna maintain that shit. 
    """
    API_SESSION: requests.Session = requests.Session()
    API_SESSION.proxies = shared.proxies
    TIMEOUT = 5
    POST_TIMEOUT = TIMEOUT
    TRIES = 5
    LOGGER = logging.getLogger("youtube")

    @classmethod
    def search_by_query(cls, query: str) -> List[MusicObject]:
        query_obj = cls.Query(query)

        #if query_obj.is_raw:
        return cls.simple_search(query_obj)
        #return cls.advanced_search(query_obj)

    @classmethod
    def simple_search(cls, query: Page.Query) -> List[Artist]:
        """
        Searches the default endpoint as is.

        NOTE: Nor YouTube neither Invidious doesn't seem to provide 
        a meaningful way of systematically parsing artist, song
        and all other fields, I rather trust in YouTube's search
        to match it well and pass channel names as artist. Note 
        that some artists don't have accounts on YouTube but 
        rather licensed the music.
        TODO: implement playlist searching or something similar to Spotube as a workaround?
        """
        endpoint = "https://yt.artemislena.eu/api/v1/search/?q={query}"

        r = cls.API_SESSION.get(endpoint.format(query=query))
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {endpoint.format(query=query.query)}")
            return []

        return [
            cls(title=getdata[1], url=getdata[2], artist=getdata[3])
            for getdata in r.json()['']
        ]
    
    @classmethod
    def _fetch_song_from_source(cls, source: Source, stop_at_level: int = 1) -> Song:
        return Song(
            title=cls(title)
        )

    @classmethod
    def _fetch_album_from_source(cls, source: Source, stop_at_level: int = 1) -> Album:
        #return Album()
        return None
    @classmethod
    def _fetch_artist_from_source(cls, source: Source, stop_at_level: int = 1) -> Artist:
        return Artist(
            artist=cls(artist)
        )

    @classmethod
    def _fetch_label_from_source(cls, source: Source, stop_at_level: int = 1) -> Label:
        #return Label()
        return None

    @classmethod
    def _get_type_of_url(cls, url: str) -> Optional[Union[Type[Song], Type[Album], Type[Artist], Type[Label]]]:
        return None

    @classmethod
    def _download_song_to_targets(cls, source: Source, target: Target, desc: str = None) -> DownloadResult:
        return DownloadResult(
            url=cls(url)
        )