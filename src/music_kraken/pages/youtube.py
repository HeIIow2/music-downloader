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

INVIDIOUS_INSTANCE = "https://yewtu.be/feed/popular"

class Youtube(Page):
    """
    The youtube downloader should use https://invidious.io/
    to make the request.
    They are an alternative frontend.

    To find an artist filter for chanel and search for
    `{artist.name} - Topic`
    and then ofc check for viable results.

    Ofc you can also implement searching songs by isrc.

    NOTE: I didn't look at the invidious api yet. If it sucks,
    feel free to use projects like youtube-dl.
    But don't implement you're own youtube client.
    I don't wanna maintain that shit. 
    """
    API_SESSION: requests.Session = requests.Session()

    SOURCE_TYPE = SourcePages.YOUTUBE
