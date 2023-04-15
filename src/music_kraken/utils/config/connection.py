from .base_classes import Section, FloatAttribute, IntAttribute, BoolAttribute, ListAttribute


class ProxAttribute(ListAttribute):
    def single_object_from_element(self, value) -> dict:
        return {
            'http': value,
            'https': value,
            'ftp': value
        }


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

        self.attribute_list = [
            self.USE_TOR,
            self.TOR_PORT,
            self.CHUNK_SIZE,
            self.SHOW_DOWNLOAD_ERRORS_THRESHOLD
        ]

        super().__init__()


CONNECTION_SECTION = ConnectionSection()
