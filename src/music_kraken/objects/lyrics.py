from typing import List
from collections import defaultdict
import pycountry

from .parents import OuterProxy
from .source import Source, SourceCollection
from .formatted_text import FormattedText
from .country import Language


class Lyrics(OuterProxy):
    COLLECTION_STRING_ATTRIBUTES = ("source_collection",)
    SIMPLE_STRING_ATTRIBUTES = {
        "text": FormattedText(),
        "language": None
    }

    text: FormattedText
    language: Language

    source_collection: SourceCollection

    _default_factories = {
        "text": FormattedText,
        "language": lambda: Language.by_alpha_2("en"),

        "source_collection": SourceCollection,
    }
