from typing import List, Optional
from enum import Enum

from ...utils.shared import YOUTUBE_MUSIC_LOGGER as LOGGER
from ...objects import Source, DatabaseObject
from ..abstract import Page
from ...objects import (
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    Label,
    Target
)


SOURCE_PAGE = SourcePages.YOUTUBE_MUSIC


class PageType(Enum):
    ARTIST = "MUSIC_PAGE_TYPE_ARTIST"
    ALBUM = "MUSIC_PAGE_TYPE_ALBUM"
    CHANNEL = "MUSIC_PAGE_TYPE_USER_CHANNEL"
    PLAYLIST = "MUSIC_PAGE_TYPE_PLAYLIST"


def parse_run_element(run_element: dict) -> Optional[DatabaseObject]:
    navigation_endpoint = run_element.get("navigationEndpoint", {}).get("browseEndpoint", {})
    
    page_type_string = navigation_endpoint.get("browseEndpointContextSupportedConfigs", {}).get("browseEndpointContextMusicConfig", {}).get("pageType", "")
    element_type = PageType(page_type_string)
    
    element_id = navigation_endpoint.get("browseId")
    element_text =  run_element.get("text")

    if element_id is None or element_text is None:
        LOGGER.warning("Couldn't find either the id or text of a Youtube music element.")
        return

    if element_type == PageType.ARTIST or element_type == PageType.CHANNEL:
        source = Source(SOURCE_PAGE, f"https://music.youtube.com/channel/{element_id}")
        return Artist(name=element_text, source_list=[source])
    
    if element_type == PageType.ALBUM or element_type == PageType.PLAYLIST:
        source = Source(SOURCE_PAGE, f"https://music.youtube.com/playlist?list={element_id}")
        return Album(title=element_text, source_list=[source])
    
    LOGGER.warning(f"Type {page_type_string} wasn't implemented.")


def parse_run_list(run_list: List[dict]) -> List[DatabaseObject]:
    music_object_list: List[DatabaseObject] = []

    for run_renderer in run_list:
        if "navigationEndpoint" not in run_renderer:
            continue

        music_object = parse_run_element(run_renderer)
        if music_object is None:
            continue

        music_object_list.append(music_object)

    return music_object_list
