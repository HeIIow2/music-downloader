from typing import List
import requests
from bs4 import BeautifulSoup
import pycountry

from ..utils.shared import (
    ENCYCLOPAEDIA_METALLUM_LOGGER as LOGGER
)

from .abstract import Page
from ..objects import (
    MusicObject,
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    ID3Timestamp,
    FormattedText,
    Label,
    Options
)
from ..utils import (
    string_processing,
    shared
)


class EncyclopaediaMetallum(Page):
    API_SESSION: requests.Session = requests.Session()
    API_SESSION.headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Connection": "keep-alive",
        "Referer": "https://musify.club/"
    }
    API_SESSION.proxies = shared.proxies

    SOURCE_TYPE = SourcePages.MUSIFY

    @classmethod
    def search_by_query(cls, query: str) -> Options:
        query_obj = cls.Query(query)

        if query_obj.is_raw:
            return cls.simple_search(query_obj)
        return cls.advanced_search(query_obj)

    @classmethod
    def advanced_search(cls, query: Page.Query) -> Options:
        if query.song is not None:
            return Options(cls.search_for_song(query=query))
        if query.album is not None:
            return Options(cls.search_for_album(query=query))
        if query.artist is not None:
            return Options(cls.search_for_artist(query=query))
        return Options

    @classmethod
    def search_for_song(cls, query: Page.Query) -> List[Song]:
        return []

    @classmethod
    def search_for_album(cls, query: Page.Query) -> List[Album]:
        return []

    @classmethod
    def search_for_artist(cls, query: Page.Query) -> List[Artist]:
        return []

    @classmethod
    def simple_search(cls, query: Page.Query) -> List[Artist]:
        return []

    @classmethod
    def fetch_album_details(cls, album: Album, flat: bool = False) -> Album:

        return album

    @classmethod
    def fetch_song_details(cls, song: Song, flat: bool = False) -> Song:
        source_list = song.source_collection.get_sources_from_page(cls.SOURCE_TYPE)
        if len(source_list) == 0:
            return song

        """
        TODO
        lyrics
        """

        return song
