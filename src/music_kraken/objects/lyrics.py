from typing import List
from collections import defaultdict
import pycountry

from .parents import DatabaseObject
from .source import Source, SourceCollection
from .formatted_text import FormattedText


class Lyrics(DatabaseObject):
    COLLECTION_ATTRIBUTES = ("source_collection",)
    SIMPLE_ATTRIBUTES = {
        "text": FormattedText(),
        "language": None
    }
    
    def __init__(
            self,
            text: FormattedText,
            language: pycountry.Languages,
            _id: str = None,
            dynamic: bool = False,
            source_list: List[Source] = None,
            **kwargs
    ) -> None:
        DatabaseObject.__init__(self, _id=_id, dynamic=dynamic, **kwargs)

        self.text: FormattedText = text or FormattedText()
        self.language: pycountry.Languages = language

        self.source_collection: SourceCollection = SourceCollection(source_list)
