from typing import List, Optional, Dict, Type
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
from ._music_object_render import parse_run_list, parse_run_element


def music_card_shelf_renderer(renderer: dict) -> List[DatabaseObject]:
    results = parse_run_list(renderer.get("title", {}).get("runs", []))

    for sub_renderer in renderer.get("contents", []):
        results.extend(parse_renderer(sub_renderer))    
    return results

def music_responsive_list_item_flex_column_renderer(renderer: dict) -> List[DatabaseObject]:
    return parse_run_list(renderer.get("text", {}).get("runs", []))


def music_responsive_list_item_renderer(renderer: dict) -> List[DatabaseObject]:
    results = []

    for i, collumn in enumerate(renderer.get("flexColumns", [])):
        _r = parse_renderer(collumn)
        if i == 0 and len(_r) == 0:
            renderer["text"] = collumn.get("musicResponsiveListItemFlexColumnRenderer", {}).get("text", {}).get("runs", [{}])[0].get("text")
            
        results.extend(_r)

    _r = parse_run_element(renderer)
    if _r is not None:
        results.append(_r)

    song_list: List[Song] = []
    album_list: List[Album] = []
    artist_list: List[Artist] = []
    _map: Dict[Type[DatabaseObject], List[DatabaseObject]] = {Song: song_list, Album: album_list, Artist: artist_list}

    for result in results:
        _map[type(result)].append(result)

    for song in song_list:
        song.album_collection.extend(album_list)
        song.main_artist_collection.extend(artist_list)
    
    for album in album_list:
        album.artist_collection.extend(artist_list)

    if len(song_list) > 0:
        return song_list
    if len(album_list) > 0:
        return album_list
    if len(artist_list) > 0:
        return artist_list
    
    return results

RENDERER_PARSERS = {
    "musicCardShelfRenderer": music_card_shelf_renderer,
    "musicResponsiveListItemRenderer": music_responsive_list_item_renderer,
    "musicResponsiveListItemFlexColumnRenderer": music_responsive_list_item_flex_column_renderer
}

def parse_renderer(renderer: dict) -> List[DatabaseObject]:
    result: List[DatabaseObject] = []

    for renderer_name, renderer in renderer.items():
        if renderer_name not in RENDERER_PARSERS:
            LOGGER.warning(f"Can't parse the renderer {renderer_name}.")
            continue
    
        result.extend(RENDERER_PARSERS[renderer_name](renderer))

    return result