from typing import Dict, List, Optional, Set, Type
from urllib.parse import urlparse, urlunparse, quote
import logging
import random
import json
from dataclasses import dataclass
import re

from ...utils.exception.config import SettingValueError
from ...utils.shared import PROXIES_LIST, YOUTUBE_MUSIC_LOGGER, DEBUG
from ...utils.config import CONNECTION_SECTION, write_config
from ...utils.functions import get_current_millis
if DEBUG:
    from ...utils.debug_utils import dump_to_file

from ...objects import Source, DatabaseObject
from ..abstract import Page
from ...objects import (
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    Label,
    Target
)
from ...connection import Connection
from ...utils.support_classes import DownloadResult

from ._list_render import parse_renderer
from .super_youtube import SuperYouTube


def get_youtube_url(path: str = "", params: str = "", query: str = "", fragment: str = "") -> str:
    return urlunparse(("https", "music.youtube.com", path, params, query, fragment))


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
    def __init__(self, logger: logging.Logger, accept_language: str):
        # https://stackoverflow.com/questions/30561260/python-change-accept-language-using-requests
        super().__init__(
            host="https://music.youtube.com/",
            logger=logger,
            hearthbeat_interval=113.25,
            header_values={
                "Accept-Language": accept_language
            }
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

    # the context in requests
    context: dict


class YoutubeMusic(SuperYouTube):
    # CHANGE
    SOURCE_TYPE = SourcePages.YOUTUBE_MUSIC
    LOGGER = YOUTUBE_MUSIC_LOGGER

    def __init__(self, *args, **kwargs):
        self.connection: YoutubeMusicConnection = YoutubeMusicConnection(logger=self.LOGGER, accept_language="en-US,en;q=0.5")
        self.credentials: YouTubeMusicCredentials = YouTubeMusicCredentials(
            api_key=CONNECTION_SECTION.YOUTUBE_MUSIC_API_KEY.object_from_value,
            ctoken="",
            context= {
                "client": {
                    "hl": "en",
                    "gl": "DE",
                    "remoteHost": "87.123.241.77",
                    "deviceMake": "",
                    "deviceModel": "",
                    "visitorData": "CgtiTUxaTHpoXzk1Zyia59WlBg%3D%3D",
                    "userAgent": self.connection.user_agent,
                    "clientName": "WEB_REMIX",
                    "clientVersion": "1.20230710.01.00",
                    "osName": "X11",
                    "osVersion": "",
                    "originalUrl": "https://music.youtube.com/",
                    "platform": "DESKTOP",
                    "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                    "configInfo": {
                        "appInstallData": "",
                        "coldConfigData": "",
                        "coldHashData": "",
                        "hotHashData": ""
                    },
                    "userInterfaceTheme": "USER_INTERFACE_THEME_DARK",
                    "timeZone": "Atlantic/Jan_Mayen",
                    "browserName": "Firefox",
                    "browserVersion": "115.0",
                    "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "deviceExperimentId": "ChxOekkxTmpnek16UTRNVFl4TkRrek1ETTVOdz09EJrn1aUGGJrn1aUG",
                    "screenWidthPoints": 584,
                    "screenHeightPoints": 939,
                    "screenPixelDensity": 1,
                    "screenDensityFloat": 1,
                    "utcOffsetMinutes": 120,
                    "musicAppInfo": {
                        "pwaInstallabilityStatus": "PWA_INSTALLABILITY_STATUS_UNKNOWN",
                        "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER",
                        "storeDigitalGoodsApiSupportStatus": {
                            "playStoreDigitalGoodsApiSupportStatus": "DIGITAL_GOODS_API_SUPPORT_STATUS_UNSUPPORTED"
                        }
                    }
                },
                "user": { "lockedSafetyMode": False },
                "request": {
                    "useSsl": True,
                    "internalExperimentFlags": [],
                    "consistencyTokenJars": []
                },
                "adSignalsInfo": {
                    "params": []
                }
            }
        )

        self.start_millis = get_current_millis()

        if self.credentials.api_key == "" or DEBUG:
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

        # context
        context_pattern = r"(?<=\"INNERTUBE_CONTEXT\":{)(.*?)(?=},\"INNERTUBE_CONTEXT_CLIENT_NAME\":)"
        found_context = False
        for context_string in re.findall(context_pattern, content):
            try:
                context = json.loads("{" + context_string + "}")
                found_context
            except json.decoder.JSONDecodeError:
                continue

            self.credentials.context = context
            break

        if not found_context:
            self.LOGGER.warning(f"Couldn't find a context for {type(self).__name__}.")

    def get_source_type(self, source: Source) -> Optional[Type[DatabaseObject]]:
        return super().get_source_type(source)
    
    def general_search(self, search_query: str) -> List[DatabaseObject]:
        search_query = search_query.strip()

        urlescaped_query: str = quote(search_query.strip().replace(" ", "+"))

        LAST_EDITED_TIME = get_current_millis() - random.randint(0, 20)
        _estimated_time = sum(len(search_query) * random.randint(50, 100) for _ in search_query.strip())
        FIRST_EDITED_TIME = LAST_EDITED_TIME - _estimated_time if LAST_EDITED_TIME - self.start_millis > _estimated_time else random.randint(50, 100)

        query_continue = "" if self.credentials.ctoken == "" else f"&ctoken={self.credentials.ctoken}&continuation={self.credentials.ctoken}"

        # construct the request
        r = self.connection.post(
            url=get_youtube_url(path="/youtubei/v1/search", query=f"key={self.credentials.api_key}&prettyPrint=false"+query_continue),
            json={
                "context": {**self.credentials.context, "adSignalsInfo":{"params":[]}},
                "query": search_query,
                "suggestStats": {
                    "clientName": "youtube-music",
                    "firstEditTimeMsec": FIRST_EDITED_TIME,
                    "inputMethod": "KEYBOARD",
                    "lastEditTimeMsec":	LAST_EDITED_TIME,
                    "originalQuery": search_query,
                    "parameterValidationStatus": "VALID_PARAMETERS",
                    "searchMethod": "ENTER_KEY",
                    "validationStatus":	"VALID",
                    "zeroPrefixEnabled": True,
                    "availableSuggestions": []
                }
            },
            headers={
                "Referer": get_youtube_url(path=f"/search", query=f"q={urlescaped_query}")
            }
        )

        self.LOGGER.debug(str(r))

        renderer_list = r.json().get("contents", {}).get("tabbedSearchResultsRenderer", {}).get("tabs", [{}])[0].get("tabRenderer").get("content", {}).get("sectionListRenderer", {}).get("contents", [])
        
        if DEBUG:
            for i, content in enumerate(renderer_list):
                dump_to_file(f"{i}-renderer.json", json.dumps(content), is_json=True, exit_after_dump=False)

        results = []

        """
        cant use fixed indices, because if something has no entries, the list dissappears
        instead I have to try parse everything, and just reject community playlists and profiles.
        """

        for renderer in renderer_list:
            results.extend(parse_renderer(renderer))

        return results

    
    def fetch_song(self, source: Source, stop_at_level: int = 1) -> Song:
        return Song()

    def fetch_album(self, source: Source, stop_at_level: int = 1) -> Album:
        return Album()

    def fetch_artist(self, source: Source, stop_at_level: int = 1) -> Artist:
        return Artist()
