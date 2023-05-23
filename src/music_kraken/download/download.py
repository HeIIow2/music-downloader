from typing import Optional, Tuple, Type, Set, Union, List

from . import page_attributes
from ..pages import Page
from ..objects import Song, Album, Artist, Label, Source

MusicObject = Union[Song, Album, Artist, Label]


class Download:
    def __init__(
            self,
            pages: Tuple[Page] = page_attributes.ALL_PAGES,
            exclude_pages=None,
            exclude_shady: bool = False,
    ) -> None:
        if exclude_pages is None:
            exclude_pages = set()

        _page_list: List[Page] = []
        _audio_page_list: List[Page] = []

        for page in pages:
            if exclude_shady and page in page_attributes.SHADY_PAGES:
                continue
            if page in exclude_pages:
                continue

            _page_list.append(page)

            if page in page_attributes.AUDIO_PAGES:
                _audio_page_list.append(page)

        self.pages: Tuple[Page] = tuple(_page_list)
        self.audio_pages: Tuple[Page] = tuple(_audio_page_list)

    def fetch_details(self, music_object: MusicObject) -> MusicObject:
        for page in self.pages:
            page.fetch_details(music_object=music_object)
        return music_object

    def fetch_source(self, source: Source) -> Optional[MusicObject]:
        source_page = page_attributes.SOURCE_PAGE_MAP[source.page_enum]

        if source_page not in self.pages:
            return

        return source_page.fetch_object_from_source(source)
