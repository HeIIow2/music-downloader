from __future__ import unicode_literals, annotations

from typing import Dict, List, Optional, Set, Type
from urllib.parse import urlparse, urlunparse, quote, parse_qs, urlencode
import logging
import random
import json
from dataclasses import dataclass
import re
from functools import lru_cache

import youtube_dl
from youtube_dl.jsinterp import JSInterpreter
from youtube_dl.extractor.youtube import YoutubeIE

from ...utils.exception.config import SettingValueError
from ...utils.config import main_settings, youtube_settings, logging_settings
from ...utils.shared import DEBUG, DEBUG_YOUTUBE_INITIALIZING
from ...utils.functions import get_current_millis

from .yt_utils.jsinterp import JSInterpreter

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
from ...utils.support_classes.download_result import DownloadResult

from ._list_render import parse_renderer
from .super_youtube import SuperYouTube


def get_youtube_url(path: str = "", params: str = "", query: str = "", fragment: str = "") -> str:
    return urlunparse(("https", "music.youtube.com", path, params, query, fragment))


class YoutubeMusicConnection(Connection):
    """
    ===heartbeat=timings=for=YOUTUBEMUSIC===
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
            heartbeat_interval=113.25,
            header_values={
                "Accept-Language": accept_language
            },
            module="youtube_music",
        )

        # cookie consent for youtube
        # https://stackoverflow.com/a/66940841/16804841 doesn't work
        for cookie_key, cookie_value in youtube_settings["youtube_music_consent_cookies"].items():
            self.session.cookies.set(
                name=cookie_key,
                value=cookie_value,
                path='/', domain='.youtube.com'
            )

    def heartbeat(self):
        r = self.get("https://music.youtube.com/verify_session", is_heartbeat=True)
        if r is None:
            self.heartbeat_failed()
            return

        string = r.text

        data = json.loads(string[string.index("{"):])
        success: bool = data["success"]

        if not success:
            self.heartbeat_failed()


@dataclass
class YouTubeMusicCredentials:
    api_key: str

    # ctoken is probably short for continue-token
    # It is probably not strictly necessary, but hey :))
    ctoken: str

    # the context in requests
    context: dict

    player_url: str

    @property
    def player_id(self):
        @lru_cache(128)
        def _extract_player_info(player_url):
            _PLAYER_INFO_RE = (
                r'/s/player/(?P<id>[a-zA-Z0-9_-]{8,})/player',
                r'/(?P<id>[a-zA-Z0-9_-]{8,})/player(?:_ias\.vflset(?:/[a-zA-Z]{2,3}_[a-zA-Z]{2,3})?|-plasma-ias-(?:phone|tablet)-[a-z]{2}_[A-Z]{2}\.vflset)/base\.js$',
                r'\b(?P<id>vfl[a-zA-Z0-9_-]+)\b.*?\.js$',
            )

            for player_re in _PLAYER_INFO_RE:
                id_m = re.search(player_re, player_url)
                if id_m:
                    break
            else:
                return

            return id_m.group('id')

        return _extract_player_info(self.player_url)


class MusicKrakenYoutubeIE(YoutubeIE):
    def __init__(self, *args, main_instance: YoutubeMusic, **kwargs):
        self.main_instance = main_instance
        super().__init__(*args, **kwargs)


class MusicKrakenYoutubeDL(youtube_dl.YoutubeDL):
    def __init__(self, main_instance: YoutubeMusic, ydl_opts: dict, **kwargs):
        self.main_instance = main_instance
        super().__init__(ydl_opts or {}, **kwargs)
        super().__enter__()

    def __del__(self):
        super().__exit__(None, None, None)




class YoutubeMusic(SuperYouTube):
    # CHANGE
    SOURCE_TYPE = SourcePages.YOUTUBE_MUSIC
    LOGGER = logging_settings["youtube_music_logger"]

    def __init__(self, *args, ydl_opts: dict = None, **kwargs):
        self.connection: YoutubeMusicConnection = YoutubeMusicConnection(
            logger=self.LOGGER,
            accept_language="en-US,en;q=0.5"
        )
        self.credentials: YouTubeMusicCredentials = YouTubeMusicCredentials(
            api_key=youtube_settings["youtube_music_api_key"],
            ctoken="",
            context=youtube_settings["youtube_music_innertube_context"],
            player_url=youtube_settings["player_url"],
        )

        self.start_millis = get_current_millis()

        if self.credentials.api_key == "" or DEBUG_YOUTUBE_INITIALIZING:
            self._fetch_from_main_page()

        SuperYouTube.__init__(self, *args, **kwargs)

        self.download_connection: Connection = Connection(
            host="https://music.youtube.com/",
            logger=self.LOGGER,
            sleep_after_404=youtube_settings["sleep_after_youtube_403"]
        )

        # https://github.com/ytdl-org/youtube-dl/blob/master/README.md#embedding-youtube-dl
        self.ydl = MusicKrakenYoutubeDL(self, ydl_opts)
        self.yt_ie = MusicKrakenYoutubeIE(downloader=self.ydl, main_instance=self)

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

        if urlparse(r.url).netloc == "consent.youtube.com":
            self.LOGGER.info(f"Making cookie consent request for {type(self).__name__}.")
            r = self.connection.post("https://consent.youtube.com/save", data={
                'gl': 'DE',
                'm': '0',
                'app': '0',
                'pc': 'ytm',
                'continue': 'https://music.youtube.com/?cbrd=1',
                'x': '6',
                'bl': 'boq_identityfrontenduiserver_20230905.04_p0',
                'hl': 'en',
                'src': '1',
                'cm': '2',
                'set_ytc': 'true',
                'set_apyt': 'true',
                'set_eom': 'false'
            })
            if r is None:
                return

            # load cookie dict from settings
            cookie_dict = youtube_settings["youtube_music_consent_cookies"]

            for cookie in r.cookies:
                cookie_dict[cookie.name] = cookie.value
            for cookie in self.connection.session.cookies:
                cookie_dict[cookie.name] = cookie.value

            # save cookies in settings
            youtube_settings["youtube_music_consent_cookies"] = cookie_dict
        else:
            self.connection.save(r, "index.html")

        r = self.connection.get("https://music.youtube.com/", name="index.html")
        if r is None:
            return

        content = r.text

        if DEBUG:
            dump_to_file(f"youtube_music_index.html", r.text, exit_after_dump=False)

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
                youtube_settings["youtube_music_api_key"] = api_key
            except SettingValueError:
                continue

            found_a_good_api_key = True
            break

        if found_a_good_api_key:
            self.LOGGER.info(f"Found a valid API-KEY for {type(self).__name__}: \"{api_key}\"")
        else:
            self.LOGGER.error(f"Couldn't find an API-KEY for {type(self).__name__}. :((")

        # context
        context_pattern = r"(?<=\"INNERTUBE_CONTEXT\":{)(.*?)(?=},\"INNERTUBE_CONTEXT_CLIENT_NAME\":)"
        found_context = False
        for context_string in re.findall(context_pattern, content, re.M):
            try:
                youtube_settings["youtube_music_innertube_context"] = json.loads("{" + context_string + "}")
                found_context = True
            except json.decoder.JSONDecodeError:
                continue

            self.credentials.context = youtube_settings["youtube_music_innertube_context"]
            break

        if not found_context:
            self.LOGGER.warning(f"Couldn't find a context for {type(self).__name__}.")

        # player url
        """
        Thanks to youtube-dl <33
        """
        player_pattern = [
            r'(?<="jsUrl":")(.*?)(?=")',
            r'(?<="PLAYER_JS_URL":")(.*?)(?=")'
        ]
        found_player_url = False

        for pattern in player_pattern:
            for player_string in re.findall(pattern, content, re.M):
                try:
                    youtube_settings["player_url"] = "https://music.youtube.com" + player_string
                    found_player_url = True
                except json.decoder.JSONDecodeError:
                    continue

                self.credentials.player_url = youtube_settings["player_url"]
                break

            if found_player_url:
                break

        if not found_player_url:
            self.LOGGER.warning(f"Couldn't find an url for the video player.")

        # ytcfg
        youtube_settings["ytcfg"] = json.loads(self._search_regex(
            r'ytcfg\.set\s*\(\s*({.+?})\s*\)\s*;',
            content,
            default='{}'
        )) or {}

    def get_source_type(self, source: Source) -> Optional[Type[DatabaseObject]]:
        return super().get_source_type(source)

    def general_search(self, search_query: str) -> List[DatabaseObject]:
        search_query = search_query.strip()

        urlescaped_query: str = quote(search_query.strip().replace(" ", "+"))

        # approximate the ammount of time it would take to type the search, because google for some reason tracks that
        LAST_EDITED_TIME = get_current_millis() - random.randint(0, 20)
        _estimated_time = sum(len(search_query) * random.randint(50, 100) for _ in search_query.strip())
        FIRST_EDITED_TIME = LAST_EDITED_TIME - _estimated_time if LAST_EDITED_TIME - self.start_millis > _estimated_time else random.randint(
            50, 100)

        query_continue = "" if self.credentials.ctoken == "" else f"&ctoken={self.credentials.ctoken}&continuation={self.credentials.ctoken}"

        # construct the request
        r = self.connection.post(
            url=get_youtube_url(path="/youtubei/v1/search",
                                query=f"key={self.credentials.api_key}&prettyPrint=false" + query_continue),
            json={
                "context": {**self.credentials.context, "adSignalsInfo": {"params": []}},
                "query": search_query,
                "suggestStats": {
                    "clientName": "youtube-music",
                    "firstEditTimeMsec": FIRST_EDITED_TIME,
                    "inputMethod": "KEYBOARD",
                    "lastEditTimeMsec": LAST_EDITED_TIME,
                    "originalQuery": search_query,
                    "parameterValidationStatus": "VALID_PARAMETERS",
                    "searchMethod": "ENTER_KEY",
                    "validationStatus": "VALID",
                    "zeroPrefixEnabled": True,
                    "availableSuggestions": []
                }
            },
            headers={
                "Referer": get_youtube_url(path=f"/search", query=f"q={urlescaped_query}")
            }
        )

        if r is None:
            return []

        renderer_list = r.json().get("contents", {}).get("tabbedSearchResultsRenderer", {}).get("tabs", [{}])[0].get(
            "tabRenderer").get("content", {}).get("sectionListRenderer", {}).get("contents", [])

        if DEBUG:
            for i, content in enumerate(renderer_list):
                dump_to_file(f"{i}-renderer.json", json.dumps(content), is_json=True, exit_after_dump=False)

        results = []

        """
        cant use fixed indices, because if something has no entries, the list disappears
        instead I have to try parse everything, and just reject community playlists and profiles.
        """

        for renderer in renderer_list:
            results.extend(parse_renderer(renderer))

        return results

    def fetch_artist(self, source: Source, stop_at_level: int = 1) -> Artist:
        artist = Artist()

        # construct the request
        url = urlparse(source.url)
        browse_id = url.path.replace("/channel/", "")

        r = self.connection.post(
            url=get_youtube_url(path="/youtubei/v1/browse", query=f"key={self.credentials.api_key}&prettyPrint=false"),
            json={
                "browseId": browse_id,
                "context": {**self.credentials.context, "adSignalsInfo": {"params": []}}
            }
        )
        if r is None:
            return artist

        if DEBUG:
            dump_to_file(f"{browse_id}.json", r.text, is_json=True, exit_after_dump=False)

        renderer_list = r.json().get("contents", {}).get("singleColumnBrowseResultsRenderer", {}).get("tabs", [{}])[
            0].get("tabRenderer", {}).get("content", {}).get("sectionListRenderer", {}).get("contents", [])

        if DEBUG:
            for i, content in enumerate(renderer_list):
                dump_to_file(f"{i}-artists-renderer.json", json.dumps(content), is_json=True, exit_after_dump=False)

        results = []

        """
        cant use fixed indices, because if something has no entries, the list dissappears
        instead I have to try parse everything, and just reject community playlists and profiles.
        """

        for renderer in renderer_list:
            results.extend(parse_renderer(renderer))

        artist.add_list_of_other_objects(results)

        return artist

    def fetch_album(self, source: Source, stop_at_level: int = 1) -> Album:
        album = Album()

        parsed_url = urlparse(source.url)
        list_id_list = parse_qs(parsed_url.query)['list']
        if len(list_id_list) <= 0:
            return album
        browse_id = list_id_list[0]

        r = self.connection.post(
            url=get_youtube_url(path="/youtubei/v1/browse", query=f"key={self.credentials.api_key}&prettyPrint=false"),
            json={
                "browseId": browse_id,
                "context": {**self.credentials.context, "adSignalsInfo": {"params": []}}
            }
        )
        if r is None:
            return album

        if DEBUG:
            dump_to_file(f"{browse_id}.json", r.text, is_json=True, exit_after_dump=False)

        renderer_list = r.json().get("contents", {}).get("singleColumnBrowseResultsRenderer", {}).get("tabs", [{}])[
            0].get("tabRenderer", {}).get("content", {}).get("sectionListRenderer", {}).get("contents", [])

        if DEBUG:
            for i, content in enumerate(renderer_list):
                dump_to_file(f"{i}-album-renderer.json", json.dumps(content), is_json=True, exit_after_dump=False)

        results = []

        """
        cant use fixed indices, because if something has no entries, the list dissappears
        instead I have to try parse everything, and just reject community playlists and profiles.
        """

        for renderer in renderer_list:
            results.extend(parse_renderer(renderer))

        album.add_list_of_other_objects(results)

        return album

    @lru_cache()
    def _extract_signature_function(self, player_url):
        r = self.connection.get(player_url)
        if r is None:
            return lambda x: None

        code = r.text

        funcname = self._search_regex((
            r'\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
            r'\b[a-zA-Z0-9]+\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
            r'\bm=(?P<sig>[a-zA-Z0-9$]{2,})\(decodeURIComponent\(h\.s\)\)',
            r'\bc&&\(c=(?P<sig>[a-zA-Z0-9$]{2,})\(decodeURIComponent\(c\)\)',
            r'(?:\b|[^a-zA-Z0-9$])(?P<sig>[a-zA-Z0-9$]{2,})\s*=\s*function\(\s*a\s*\)\s*{\s*a\s*=\s*a\.split\(\s*""\s*\)(?:;[a-zA-Z0-9$]{2}\.[a-zA-Z0-9$]{2}\(a,\d+\))?',
            r'(?P<sig>[a-zA-Z0-9$]+)\s*=\s*function\(\s*a\s*\)\s*{\s*a\s*=\s*a\.split\(\s*""\s*\)',
            # Obsolete patterns
            r'("|\')signature\1\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
            r'\.sig\|\|(?P<sig>[a-zA-Z0-9$]+)\(',
            r'yt\.akamaized\.net/\)\s*\|\|\s*.*?\s*[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?:encodeURIComponent\s*\()?\s*(?P<sig>[a-zA-Z0-9$]+)\(',
            r'\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
            r'\b[a-zA-Z0-9]+\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
            r'\bc\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\('
        ),
            code, group='sig')

        jsi = JSInterpreter(code)
        initial_function = jsi.extract_function(funcname)

        return lambda s: initial_function([s])

    def _decrypt_signature(self, video_id, s):
        print(youtube_settings["player_url"])
        res = self._extract_signature_function(player_url=youtube_settings["player_url"])
        test_string = ''.join(map(str, range(len(s))))
        cache_spec = [ord(c) for c in res(test_string)]
        signing_func = lambda _s: ''.join(_s[i] for i in cache_spec)
        return signing_func(s)

    def _parse_adaptive_formats(self, data: list, video_id) -> dict:
        best_format = None
        best_bitrate = 0

        def parse_format(fmt: dict):
            fmt_url = fmt.get('url')

            if not fmt_url:
                sc = parse_qs(possible_format["signatureCipher"])
                print(sc["s"][0])
                signature = self._decrypt_signature(video_id, sc['s'][0])
                print(signature)

                tmp = sc.get("sp", ["sig"])
                sig_key = "signature" if len(tmp) <= 0 else tmp[-1]

                fmt_url = sc.get("url", [None])[0]

                ftm_parsed = urlparse(fmt_url)
                q = parse_qs(ftm_parsed.query)
                q[sig_key] = [signature]
                print(json.dumps(q, indent=4))
                print(sig_key)
                query_str = urlencode(q)
                print(query_str)

                fmt_url = urlunparse((
                    ftm_parsed.scheme,
                    ftm_parsed.netloc,
                    ftm_parsed.path,
                    ftm_parsed.params,
                    query_str,
                    ftm_parsed.fragment
                ))

                """
                    if not isinstance(url, tuple):
                        url = compat_urllib_parse.urlparse(url)
                    query = kwargs.pop('query_update', None)
                    if query:
                        qs = compat_parse_qs(url.query)
                        qs.update(query)
                        kwargs['query'] = compat_urllib_parse_urlencode(qs, True)
                        kwargs = compat_kwargs(kwargs)
                    return compat_urllib_parse.urlunparse(url._replace(**kwargs))
                """

            return {
                "bitrate": fmt.get("bitrate"),
                "url": fmt_url
            }

        for possible_format in sorted(data, key=lambda x: x.get("bitrate", 0)):
            if best_bitrate <= 0:
                # no format has been found yet
                best_format = possible_format

            if possible_format.get('targetDurationSec') or possible_format.get('drmFamilies'):
                continue

            mime_type: str = possible_format["mimeType"]
            if not mime_type.startswith("audio"):
                continue

            bitrate = int(possible_format.get("bitrate", 0))

            if bitrate > best_bitrate:
                best_bitrate = bitrate
                best_format = possible_format

            if bitrate >= main_settings["bitrate"]:
                break

        return parse_format(best_format)

    def fetch_song(self, source: Source, stop_at_level: int = 1) -> Song:
        # implement the functionality yt_dl provides
        ydl_res = self.yt_ie._real_extract(source.url)
        print(ydl_res)

        source.audio_url = ydl_res.get("formats")[0].get("url")
        song = Song(
            title=ydl_res.get("title"),
            source_list=[source],
        )
        return song

        parsed_url = urlparse(source.url)
        video_id = parse_qs(parsed_url.query)['v']
        if len(video_id) <= 0:
            return song
        browse_id = video_id[0]

        r = self.connection.post(
            url=get_youtube_url(path="/youtubei/v1/player", query=f"key={self.credentials.api_key}&prettyPrint=false"),
            json={
                "videoId": browse_id,
                "context": {**self.credentials.context, "adSignalsInfo": {"params": []}}
            }
        )
        if r is None:
            return song

        data = r.json()

        dump_to_file("yt_video_overview.json", data, exit_after_dump=False)

        available_formats = data.get("streamingData", {}).get("adaptiveFormats", [])

        if len(available_formats) > 0:
            source.audio_url = self._parse_adaptive_formats(available_formats, video_id=browse_id).get("url")

        return song

    def download_song_to_target(self, source: Source, target: Target, desc: str = None) -> DownloadResult:
        if source.audio_url is None:
            self.fetch_song(source)

        if source.audio_url is None:
            self.LOGGER.warning(f"Couldn't fetch the audio source with the innertube api, falling back to invidious.")
            return super().download_song_to_target(source, target)

        print(source.audio_url)
        return self.download_connection.stream_into(source.audio_url, target, description=desc, headers={
            "Host": "rr1---sn-cxaf0x-nugl.googlevideo.com"
        })

    def __del__(self):
        self.ydl.__exit__()
