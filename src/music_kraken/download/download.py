from typing import Optional, Tuple, Type, Set, Union, List

from .page_attributes import Pages
from ..pages import Page
from ..objects import Song, Album, Artist, Label, Source

MusicObject = Union[Song, Album, Artist, Label]


class Download:
    def __init__(
            self,
            exclude_pages: Set[Type[Page]] = None, 
            exclude_shady: bool = False
    ) -> None:

        self.pages: Pages = Pages(exclude_pages=exclude_pages, exclude_shady=exclude_shady)

    def fetch_details(self, music_object: MusicObject) -> MusicObject:
        for page in self.pages:
            page.fetch_details(music_object=music_object)
        return music_object

    def fetch_source(self, source: Source) -> Optional[MusicObject]:
        source_page = page_attributes.SOURCE_PAGE_MAP[source.page_enum]

        if source_page not in self.pages:
            return

        return source_page.fetch_object_from_source(source)
