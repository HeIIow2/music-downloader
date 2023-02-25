from typing import List

import pycountry

from .parents import DatabaseObject
from .source import SourceAttribute, Source
from .metadata import MetadataAttribute
from .formatted_text import FormattedText


class Lyrics(DatabaseObject, SourceAttribute, MetadataAttribute):
    def __init__(
            self,
            text: FormattedText,
            language: pycountry.Languages,
            _id: str = None,
            dynamic: bool = False,
            source_list: List[Source] = None,
            **kwargs
    ) -> None:
        DatabaseObject.__init__(_id=_id, dynamic=dynamic)

        self.text: FormattedText = text
        self.language: pycountry.Languages = language

        if source_list is not None:
            self.source_list = source_list
