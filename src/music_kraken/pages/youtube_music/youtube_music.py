from typing import Dict, List, Optional, Set, Type
from urllib.parse import urlparse, urlunparse, quote, parse_qs
import logging
import random
import json
from dataclasses import dataclass
import re

from ...utils.exception.config import SettingValueError
from ...utils.config import main_settings, youtube_settings, logging_settings
from ...utils.shared import DEBUG, DEBUG_YOUTUBE_INITIALIZING
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
            }
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


class YoutubeMusic(SuperYouTube):
    # CHANGE
    SOURCE_TYPE = SourcePages.YOUTUBE_MUSIC
    LOGGER = logging_settings["youtube_music_logger"]

    def __init__(self, *args, **kwargs):
        self.connection: YoutubeMusicConnection = YoutubeMusicConnection(logger=self.LOGGER,
                                                                         accept_language="en-US,en;q=0.5")
        self.credentials: YouTubeMusicCredentials = YouTubeMusicCredentials(
            api_key=youtube_settings["youtube_music_api_key"],
            ctoken="",
            context=youtube_settings["youtube_music_innertube_context"]
        )

        self.start_millis = get_current_millis()

        if self.credentials.api_key == "" or DEBUG_YOUTUBE_INITIALIZING:
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

        r = self.connection.get("https://music.youtube.com/")
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

    @staticmethod
    def _parse_adaptive_formats(data: list) -> str:
        best_url = None
        audio_format = None
        best_bitrate = 0

        def decode_url(_format: dict):
            """
            s=0%3Dw9hlenzIQkU5qD55flWqkO-wn8G6CJxI%3Dn9_OSUAUh3AiACkI5TNetQixuV6PJAxH-NFqGWGQCivQMkqprwyv8z2NAhIQRwsSdQfJAfJA
            sp=sig
            url=https://rr1---sn-cxaf0x-nugl.googlevideo.com/videoplayback%3Fexpire%3D1705426390%26ei%3DdmmmZZK1OYf41gL26KGwDg%26ip%3D129.143.170.58%26id%3Do-APgHuP61UnxvMxskECWmga1BRWYDFv91DMB7E6R_b_CG%26itag%3D18%26source%3Dyoutube%26requiressl%3Dyes%26xpc%3DEgVo2aDSNQ%253D%253D%26mh%3D_V%26mm%3D31%252C29%26mn%3Dsn-cxaf0x-nugl%252Csn-4g5edndd%26ms%3Dau%252Crdu%26mv%3Dm%26mvi%3D1%26pl%3D16%26pcm2%3Dyes%26gcr%3Dde%26initcwndbps%3D1737500%26spc%3DUWF9f6gk6WFPUFJZkjGIeb9q8NjPmmcsXzCp%26vprv%3D1%26svpuc%3D1%26mime%3Dvideo%252Fmp4%26ns%3DJnQgwQe-JazkZpURVB2rmlUQ%26cnr%3D14%26ratebypass%3Dyes%26dur%3D170.643%26lmt%3D1697280536047282%26mt%3D1705404526%26fvip%3D4%26fexp%3D24007246%26c%3DWEB_REMIX%26txp%3D2318224%26n%3DEq7jcRmeC89oLlbr%26sparams%3Dexpire%252Cei%252Cip%252Cid%252Citag%252Csource%252Crequiressl%252Cxpc%252Cpcm2%252Cgcr%252Cspc%252Cvprv%252Csvpuc%252Cmime%252Cns%252Ccnr%252Cratebypass%252Cdur%252Clmt%26lsparams%3Dmh%252Cmm%252Cmn%252Cms%252Cmv%252Cmvi%252Cpl%252Cinitcwndbps%26lsig%3DAAO5W4owRQIhAOJSldsMn2QA8b-rMr8mJoPr-9-8piIMe6J-800YB0DiAiBKLBHGfr-a6d87K0-WbsJzVf9f2DhYgv0vcntWvHmvGA%253D%253D"
            :param _format:
            :return:
            """
            sc = parse_qs(_format["signatureCipher"])

            fmt_url = sc["url"][0]
            encrypted_sig = sc['s'][0]

            if not (sc and fmt_url and encrypted_sig):
                return

            """
            if not player_url:
                player_url = self._extract_player_url(webpage)
            if not player_url:
                return
            
            signature = self._decrypt_signature(sc['s'][0], video_id, player_url)
            sp = try_get(sc, lambda x: x['sp'][0]) or 'signature'
            fmt_url += '&' + sp + '=' + signature
            """

        for possible_format in data:
            _url_list = parse_qs(possible_format["signatureCipher"])["url"]
            if len(_url_list) <= 0:
                continue

            url = _url_list[0]
            if best_url is None:
                best_url = url

            mime_type: str = possible_format["mimeType"]
            if not mime_type.startswith("audio"):
                continue

            bitrate = int(possible_format.get("bitrate", 0))

            if bitrate >= main_settings["bitrate"]:
                best_bitrate = bitrate
                audio_format = possible_format
                best_url = url
                break

            if bitrate > best_bitrate:
                best_bitrate = bitrate
                audio_format = possible_format
                best_url = url

        return best_url

    def fetch_song(self, source: Source, stop_at_level: int = 1) -> Song:
        """
        curl 'https://music.youtube.com/youtubei/v1/player?key=AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30&prettyPrint=false'
            --compressed -X POST
            -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0'
            -H 'Accept: */*'
            -H 'Accept-Language: en-US,en;q=0.5'
            -H 'Accept-Encoding: gzip, deflate, br'
             -H 'Content-Type: application/json'
             -H 'Referer: https://music.youtube.com/'
             -H 'X-Goog-Visitor-Id: CgtHdmkzbGhaMDltVSj4j5mtBjIKCgJERRIEEgAgOA%3D%3D'
             -H 'X-Youtube-Bootstrap-Logged-In: false'
             -H 'X-Youtube-Client-Name: 67' -H 'X-Youtube-Client-Version: 1.20240103.01.00'
             -H 'Origin: https://music.youtube.com'
             -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' -H 'Connection: keep-alive' -H 'Alt-Used: music.youtube.com'
            -H 'Cookie: SOCS=CAISNQgREitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjQwMTA5LjA1X3AwGgJlbiACGgYIgI6XrQY; YSC=r46McyPx8dE; VISITOR_PRIVACY_METADATA=CgJERRIEEgAgOA%3D%3D; CONSENT=PENDING+663; VISITOR_INFO1_LIVE=Gvi3lhZ09mU; _gcl_au=1.1.396177275.1705396217; ST-1hw5vco=csn=MC4xNTI3OTkwMzQyOTc1MzQ2&itct=CNgDEMn0AhgDIhMItMS6_cfhgwMVDMtCBR1u5wb6' -H 'TE: trailers'
            --data-raw '{
                "videoId":"QeQrfsqPMCs",
                "context":{"client":{"hl":"en","gl":"DE","remoteHost":"129.143.170.58","deviceMake":"","deviceModel":"","visitorData":"CgtHdmkzbGhaMDltVSj4j5mtBjIKCgJERRIEEgAgOA%3D%3D","userAgent":"Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0,gzip(gfe)","clientName":"WEB_REMIX","clientVersion":"1.20240103.01.00","osName":"X11","osVersion":"","originalUrl":"https://music.youtube.com/?cbrd=1","platform":"DESKTOP","clientFormFactor":"UNKNOWN_FORM_FACTOR","configInfo":{"appInstallData":"CPiPma0GEL2ZsAUQqJqwBRCmgbAFEP24_RIQjaKwBRDNlbAFENWIsAUQmaSwBRD6p7AFEL75rwUQmvCvBRDT4a8FEL2KsAUQrtT-EhC36v4SENnJrwUQnouwBRDJ968FEJP8rwUQuIuuBRDM364FEIiHsAUQ0I2wBRDnuq8FEPOhsAUQ2piwBRDMrv4SEIjjrwUQooGwBRDuorAFEM6osAUQ6-j-EhC3nbAFEKXC_hIQ9fmvBRDh8q8FEJmUsAUQt--vBRD8hbAFEKigsAUQrLevBRC_o7AFEOuTrgUQqfevBRDd6P4SEJj8_hIQ6YywBRC9tq4FEOupsAUQ5LP-EhDfhP8SEOrDrwUQqKGwBRC8-a8FEPKYsAU%3D"},"browserName":"Firefox","browserVersion":"121.0","acceptHeader":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8","deviceExperimentId":"ChxOek15TkRZeU1EazNOalE0TXpVNU1EQXhOZz09EPiPma0GGPiPma0G","screenWidthPoints":780,"screenHeightPoints":638,"screenPixelDensity":2,"screenDensityFloat":2,"utcOffsetMinutes":60,"userInterfaceTheme":"USER_INTERFACE_THEME_DARK","timeZone":"Europe/Berlin","playerType":"UNIPLAYER","tvAppInfo":{"livingRoomAppMode":"LIVING_ROOM_APP_MODE_UNSPECIFIED"},"clientScreen":"WATCH_FULL_SCREEN"},"user":{"lockedSafetyMode":false},"request":{"useSsl":true,"internalExperimentFlags":[],"consistencyTokenJars":[]},"clientScreenNonce":"MC4xNTI3OTkwMzQyOTc1MzQ2","adSignalsInfo":{"params":[{"key":"dt","value":"1705396224619"},{"key":"flash","value":"0"},{"key":"frm","value":"0"},{"key":"u_tz","value":"60"},{"key":"u_his","value":"5"},{"key":"u_h","value":"800"},{"key":"u_w","value":"1280"},{"key":"u_ah","value":"769"},{"key":"u_aw","value":"1280"},{"key":"u_cd","value":"24"},{"key":"bc","value":"31"},{"key":"bih","value":"638"},{"key":"biw","value":"780"},{"key":"brdim","value":"0,31,0,31,1280,31,1280,769,780,638"},{"key":"vis","value":"1"},{"key":"wgl","value":"true"},{"key":"ca_type","value":"image"}]},"clickTracking":{"clickTrackingParams":"CNgDEMn0AhgDIhMItMS6_cfhgwMVDMtCBR1u5wb6"}},"playbackContext":{"contentPlaybackContext":{"html5Preference":"HTML5_PREF_WANTS","lactMilliseconds":"22","referer":"https://music.youtube.com/","signatureTimestamp":19732,"autoCaptionsDefaultOn":false,"mdxContext":{}}},"cpn":"Aqv99K7Z_3tj9ACA","playlistId":"RDAMVMQeQrfsqPMCs","captionParams":{},"serviceIntegrityDimensions":{"poToken":"MnQLhidwfIVPEAu-woG_SQU69mfPclEz7kVUmC1dNP8EQN7NNyVdF3KcVIuKRKrcXlwOXEQg3hc5qXSBbbQU_M7lxx9zgQMelv9iZwWfWlLyI9RoZXB1wipAYHWNzxu7rMqDwRn5M6WS4RRIeHcld9P_YZRYdg=="}
            }'
        :param source:
        :param stop_at_level:
        :return:
        """
        song = Song(source_list=[
            source
        ])

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
            source.audio_url = self._parse_adaptive_formats(available_formats)

        return song

    def download_song_to_target(self, source: Source, target: Target, desc: str = None) -> DownloadResult:
        if source.audio_url is None:
            self.fetch_song(source)

        if source.audio_url is None:
            self.LOGGER.warning(f"Couldn't fetch the audio source with the innertube api, falling back to invidious.")
            return super().download_song_to_target(source, target)

        print(source.audio_url)
        return self.download_connection.stream_into(source.audio_url, target, description=desc, raw_url=True)
