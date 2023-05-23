from typing import Optional, Tuple, Type, Set, Union, List

from . import page_attributes
from ..abstract import Page
from ...objects import Song, Album, Artist, Label, Source

MusicObject = Union[Song, Album, Artist, Label]


class Download:
    def __init__(
            self,
            pages: Tuple[Type[Page]] = page_attributes.ALL_PAGES,
            exclude_pages: Set[Type[Page]] = set(),
            exclude_shady: bool = False,
    ) -> None:
        _page_list: List[Type[Page]] = []
        _audio_page_list: List[Type[Page]] = []

        for page in pages:
            if exclude_shady and page in page_attributes.SHADY_PAGES:
                continue
            if page in exclude_pages:
                continue

            _page_list.append(page)

            if page in page_attributes.AUDIO_PAGES:
                _audio_page_list.append(page)

        self.pages: Tuple[Type[Page]] = tuple(_page_list)
        self.audio_pages: Tuple[Type[Page]] = tuple(_audio_page_list)

    def fetch_details(self, music_object: MusicObject) -> MusicObject:
        for page in self.pages:
            page.fetch_details(music_object=music_object)
        return music_object

    def fetch_source(self, source: Source) -> Optional[MusicObject]:
        source_page = page_attributes.SOURCE_PAGE_MAP[source.page_enum]

        if source_page not in self.pages:
            return

        return source_page.fetch_object_from_source(source)
