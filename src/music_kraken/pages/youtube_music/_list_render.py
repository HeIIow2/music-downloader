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
from ._music_object_render import parse_run_list


def music_card_shelf_renderer(renderer: dict) -> List[DatabaseObject]:
    return parse_run_list(renderer.get("title", {}).get("runs", []))


RENDERER_PARSERS = {
    "musicCardShelfRenderer": music_card_shelf_renderer
}

def parse_renderer(renderer: dict) -> List[DatabaseObject]:
    result: List[DatabaseObject] = []

    for renderer_name, renderer in renderer.items():
        if renderer_name not in RENDERER_PARSERS:
            LOGGER.warning(f"Can't parse the renderer {renderer_name}.")
            continue
    
        result.extend(RENDERER_PARSERS[renderer_name](renderer))

    return result