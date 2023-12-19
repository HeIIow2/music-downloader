from typing import List
from collections import defaultdict
import pycountry

from .parents import OuterProxy
from .source import Source, SourceCollection
from .formatted_text import FormattedText


class Lyrics(OuterProxy):
    COLLECTION_STRING_ATTRIBUTES = ("source_collection",)
    SIMPLE_STRING_ATTRIBUTES = {
        "text": FormattedText(),
        "language": None
    }
    
    def __init__(
            self,
            text: FormattedText,
            language: pycountry.Languages = pycountry.languages.get(alpha_2="en"),
            _id: str = None,
            dynamic: bool = False,
            source_list: List[Source] = None,
            **kwargs
    ) -> None:
        super().__init__(_id=_id, dynamic=dynamic, **kwargs)

        self.text: FormattedText = text or FormattedText()
        self.language: pycountry.Languages = language

        self.source_collection: SourceCollection = SourceCollection(source_list)
