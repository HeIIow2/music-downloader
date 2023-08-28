from urllib.parse import urlparse, ParseResult
import re

from ..base_classes import Section, FloatAttribute, IntAttribute, BoolAttribute, ListAttribute, StringAttribute
from ...regex import URL_PATTERN
from ...exception.config import SettingValueError


class ProxAttribute(ListAttribute):
    def single_object_from_element(self, value) -> dict:
        return {
            'http': value,
            'https': value,
            'ftp': value
        }


class UrlStringAttribute(StringAttribute):
    def validate(self, value: str):
        v = value.strip()
        url = re.match(URL_PATTERN, v)
        if url is None:
            raise SettingValueError(
                setting_name=self.name,
                setting_value=v,
                rule="has to be a valid url"
            )

    @property
    def object_from_value(self) -> ParseResult:
        return urlparse(self.value)


class UrlListAttribute(ListAttribute):
    def validate(self, value: str):
        v = value.strip()
        url = re.match(URL_PATTERN, v)
        if url is None:
            raise SettingValueError(
                setting_name=self.name,
                setting_value=v,
                rule="has to be a valid url"
            )
            
    def single_object_from_element(self, value: str):
        return urlparse(value)



class ConnectionSection(Section):
    def __init__(self):
        self.PROXIES = ProxAttribute(
            name="proxies",
            description="Set your proxies.\n"
                        "Must be valid for http, as well as https.",
            value=[]
        )

        self.USE_TOR = BoolAttribute(
            name="tor",
            description="Route ALL traffic through Tor.\n"
                        "If you use Tor, make sure the Tor browser is installed, and running."
                        "I can't guarantee maximum security though!",
            value="false"
        )
        self.TOR_PORT = IntAttribute(
            name="tor_port",
            description="The port, tor is listening. If tor is already working, don't change it.",
            value="9150"
        )
        self.CHUNK_SIZE = IntAttribute(
            name="chunk_size",
            description="Size of the chunks that are streamed.",
            value="1024"
        )
        self.SHOW_DOWNLOAD_ERRORS_THRESHOLD = FloatAttribute(
            name="show_download_errors_threshold",
            description="If the percentage of failed downloads goes over this threshold,\n"
                        "all the error messages are shown.",
            value="0.3"
        )

        # INVIDIOUS INSTANCES LIST
        self.INVIDIOUS_INSTANCE = UrlStringAttribute(
            name="invidious_instance",
            description="This is an attribute, where you can define the invidious instances,\n"
                        "the youtube downloader should use.\n"
                        "Here is a list of active ones: https://docs.invidious.io/instances/\n"
                        "Instances that use cloudflare or have source code changes could cause issues.\n"
                        "Hidden instances (.onion) will only work, when setting 'tor=true'.",
            value="https://yt.artemislena.eu/"
        )
        
        self.PIPED_INSTANCE = UrlStringAttribute(
            name="piped_instance",
            description="This is an attribute, where you can define the pioed instances,\n"
                        "the youtube downloader should use.\n"
                        "Here is a list of active ones: https://github.com/TeamPiped/Piped/wiki/Instances\n"
                        "Instances that use cloudflare or have source code changes could cause issues.\n"
                        "Hidden instances (.onion) will only work, when setting 'tor=true'.",
            value="https://pipedapi.kavin.rocks"
        )

        self.SLEEP_AFTER_YOUTUBE_403 = FloatAttribute(
            name="sleep_after_youtube_403",
            description="The time to wait, after youtube returned 403 (in seconds)",
            value="20"
        )

        self.YOUTUBE_MUSIC_API_KEY = StringAttribute(
            name="youtube_music_api_key",
            description="This is the API key used by YouTube-Music internally.\nDw. if it is empty, Rachel will fetch it automatically for you <333\n(she will also update outdated api keys/those that don't work)",
            value="AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30"
        )

        self.YOUTUBE_MUSIC_CLEAN_DATA = BoolAttribute(
            name="youtube_music_clean_data",
            description="If set to true, it exclusively fetches artists/albums/songs, not things like user channels etc.",
            value="true"
        )
        
        self.ALL_YOUTUBE_URLS = UrlListAttribute(
            name="youtube_url",
            description="This is used to detect, if an url is from youtube, or any alternativ frontend.\n"
                        "If any instance seems to be missing, run music kraken with the -f flag.",
            value=[
                "https://www.youtube.com/",
                "https://www.youtu.be/",
                "https://redirect.invidious.io/",
                "https://piped.kavin.rocks/"
            ]
        )
        
        self.SPONSOR_BLOCK = BoolAttribute(
            name="use_sponsor_block",
            value="true",
            description="Use sponsor block to remove adds or simmilar from the youtube videos."
        )

        self.attribute_list = [
            self.USE_TOR,
            self.TOR_PORT,
            self.CHUNK_SIZE,
            self.SHOW_DOWNLOAD_ERRORS_THRESHOLD,
            self.INVIDIOUS_INSTANCE,
            self.PIPED_INSTANCE,
            self.SLEEP_AFTER_YOUTUBE_403,
            self.YOUTUBE_MUSIC_API_KEY,
            self.YOUTUBE_MUSIC_CLEAN_DATA,
            self.ALL_YOUTUBE_URLS,
            self.SPONSOR_BLOCK
        ]

        super().__init__()


CONNECTION_SECTION = ConnectionSection()
