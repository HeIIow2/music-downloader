from urllib.parse import urlparse
import re

from .base_classes import Section, FloatAttribute, IntAttribute, BoolAttribute, ListAttribute, StringAttribute
from ..regex import URL_PATTERN
from ..exception.config import SettingValueError


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
            description="This is a List, where you can define the invidious instances,\n"
                        "the youtube downloader should use.\n"
                        "Here is a list of active ones: https://docs.invidious.io/instances/\n"
                        "Instances that use cloudflare or have source code changes could cause issues.\n"
                        "Hidden instances (.onion) will only work, when setting 'tor=true'.",
            value="https://yt.artemislena.eu/"
        )
        # INVIDIOUS PROXY
        self.INVIDIOUS_PROXY_VIDEOS = BoolAttribute(
            name="invidious_proxy_video",
            value="false",
            description="Downloads the videos using the given instances."
        )

        self.attribute_list = [
            self.USE_TOR,
            self.TOR_PORT,
            self.CHUNK_SIZE,
            self.SHOW_DOWNLOAD_ERRORS_THRESHOLD,
            self.INVIDIOUS_INSTANCE,
            self.INVIDIOUS_PROXY_VIDEOS
        ]

        super().__init__()


CONNECTION_SECTION = ConnectionSection()
