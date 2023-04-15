import logging
from typing import Callable

from .base_classes import SingleAttribute, StringAttribute, Section, FloatAttribute, Description, IntAttribute, EmptyLine, BoolAttribute


class ConnectionSection(Section):
    def __init__(self):
        self.USE_TOR = BoolAttribute(
            name="tor",
            description="Route ALL traffic through Tor.\nNo guarantee though!",
            value="false"
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
            self.CHUNK_SIZE,
            self.SHOW_DOWNLOAD_ERRORS_THRESHOLD
        ]

        super().__init__()


CONNECTION_SECTION = ConnectionSection()
