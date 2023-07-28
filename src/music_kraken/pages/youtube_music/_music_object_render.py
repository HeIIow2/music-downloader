from typing import List, Optional
from enum import Enum

from ...utils.shared import YOUTUBE_MUSIC_LOGGER as LOGGER, YOUTUBE_MUSIC_CLEAN_DATA
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
    SONG = "MUSIC_VIDEO_TYPE_ATV"
    VIDEO = "MUSIC_VIDEO_TYPE_UGC"
    OFFICIAL_MUSIC_VIDEO = "MUSIC_VIDEO_TYPE_OMV"


def parse_run_element(run_element: dict) -> Optional[DatabaseObject]:
    if "navigationEndpoint" not in run_element:
        return
    
    _temp_nav = run_element.get("navigationEndpoint", {})
    is_video = "watchEndpoint" in _temp_nav

    navigation_endpoint = _temp_nav.get("watchEndpoint" if is_video else "browseEndpoint", {})
    
    element_type = PageType.SONG
    page_type_string = navigation_endpoint.get("watchEndpointMusicSupportedConfigs", {}).get("watchEndpointMusicConfig", {}).get("musicVideoType", "")
    if not is_video:
        page_type_string = navigation_endpoint.get("browseEndpointContextSupportedConfigs", {}).get("browseEndpointContextMusicConfig", {}).get("pageType", "")
    element_type = PageType(page_type_string)
    
    element_id = navigation_endpoint.get("videoId" if is_video else "browseId")
    element_text =  run_element.get("text")

    if element_id is None or element_text is None:
        LOGGER.warning("Couldn't find either the id or text of a Youtube music element.")
        return
    
    if element_type == PageType.SONG or (element_type == PageType.VIDEO and not YOUTUBE_MUSIC_CLEAN_DATA) or (element_type == PageType.OFFICIAL_MUSIC_VIDEO and not YOUTUBE_MUSIC_CLEAN_DATA):
        source = Source(SOURCE_PAGE, f"https://music.youtube.com/watch?v={element_id}")
        return Song(title=element_text, source_list=[source])

    if element_type == PageType.ARTIST or (element_type == PageType.CHANNEL and not YOUTUBE_MUSIC_CLEAN_DATA):
        source = Source(SOURCE_PAGE, f"https://music.youtube.com/channel/{element_id}")
        return Artist(name=element_text, source_list=[source])
    
    if element_type == PageType.ALBUM or (element_type == PageType.PLAYLIST and not YOUTUBE_MUSIC_CLEAN_DATA):
        source = Source(SOURCE_PAGE, f"https://music.youtube.com/playlist?list={element_id}")
        return Album(title=element_text, source_list=[source])
    
    LOGGER.debug(f"Type {page_type_string} wasn't implemented.")


def parse_run_list(run_list: List[dict]) -> List[DatabaseObject]:
    music_object_list: List[DatabaseObject] = []

    for run_renderer in run_list:
        music_object = parse_run_element(run_renderer)
        if music_object is None:
            continue

        music_object_list.append(music_object)

    return music_object_list
