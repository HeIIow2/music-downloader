from typing import List, Optional, Type
from urllib.parse import urlparse
import logging
from enum import Enum


from ..objects import Source, DatabaseObject
from .abstract import Page
from ..objects import (
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    Label,
    Target
)
from ..connection import Connection
from ..utils.support_classes import DownloadResult
from ..utils.config import main_settings, logging_settings
from ..utils.shared import DEBUG
if DEBUG:
    from ..utils.debug_utils import dump_to_file


class BandcampTypes(Enum):
    ARTIST = "b"
    ALBUM = "a"
    SONG = "t"


class Bandcamp(Page):
    # CHANGE
    SOURCE_TYPE = SourcePages.BANDCAMP
    LOGGER = logging_settings["bandcamp_logger"]

    def __init__(self, *args, **kwargs):
        self.connection: Connection = Connection(
            host="https://bandcamp.com/",
            logger=self.LOGGER
        )
        
        super().__init__(*args, **kwargs)

    def get_source_type(self, source: Source) -> Optional[Type[DatabaseObject]]:
        parsed_url = urlparse(source.url)

        if parsed_url.path == "":
            return Artist
        if parsed_url.path.startswith("/album/"):
            return Album
        if parsed_url.path.startswith("/track/"):
            return Song
        
        return super().get_source_type(source)

    def _parse_autocomplete_api_result(self, data: dict) -> DatabaseObject:
        try:
            object_type = BandcampTypes(data["type"])
        except ValueError:
            print(data["type"])
            return

        url = data["item_url_root"]
        if "item_url_path" in data:
            url = data["item_url_path"]

        source_list = [Source(self.SOURCE_TYPE, url)]
        name = data["name"]

        if data.get("is_label", False):
            return Label(
                name=name,
                source_list=source_list
            )

        if object_type is BandcampTypes.ARTIST:
            return Artist(
                name=name,
                source_list=source_list
            )

        if object_type is BandcampTypes.ALBUM:
            return Album(
                title=name,
                source_list=source_list,
                artist_list=[
                    Artist(
                        name=data["band_name"],
                        source_list=[
                            Source(self.SOURCE_TYPE, data["item_url_root"])
                        ]
                    )
                ]
            )

        if object_type is BandcampTypes.SONG:
            return Song(
                title=name,
                source_list=source_list,
                main_artist_list=[
                    Artist(
                        name=data["band_name"],
                        source_list=[
                            Source(self.SOURCE_TYPE, data["item_url_root"])
                        ]
                    )
                ]
            )
    
    def general_search(self, search_query: str, filter_string: str = "") -> List[DatabaseObject]:
        results = []

        r = self.connection.post("https://bandcamp.com/api/bcsearch_public_api/1/autocomplete_elastic", json={
            "fan_id": None,
            "full_page": True,
            "search_filter": filter_string,
            "search_text": search_query,
        })
        if r is None:
            return results

        if DEBUG:
            dump_to_file("bandcamp_response.json", r.text, is_json=True, exit_after_dump=False)

        data = r.json()

        for element in data.get("auto", {}).get("results", []):
            r = self._parse_autocomplete_api_result(element)
            if r is not None:
                results.append(r)

        return results
    
    def label_search(self, label: Label) -> List[Label]:
        return self.general_search(label.name, filter_string="b")
    
    def artist_search(self, artist: Artist) -> List[Artist]:
        return self.general_search(artist.name, filter_string="b")
    
    def album_search(self, album: Album) -> List[Album]:
        return self.general_search(album.title, filter_string="a")
    
    def song_search(self, song: Song) -> List[Song]:
        return self.general_search(song.title, filter_string="t")
    

    def fetch_artist(self, source: Source, stop_at_level: int = 1) -> Artist:
        artist = Artist()

        r = self.connection.get(source.url)
        if r is None:
            return artist
        
        soup = self.get_soup_from_response(r)
        data_container = soup.find("div", {"id": "pagedata"})
        data = data_container["data-blob"]
        
        if DEBUG:
            dump_to_file("artist_page.html", r.text, exit_after_dump=False)
            dump_to_file("bandcamp_artis.json", data, is_json=True, exit_after_dump=False)

        return artist
    
    def fetch_song(self, source: Source, stop_at_level: int = 1) -> Song:
        print(source)
        return Song()

    def fetch_album(self, source: Source, stop_at_level: int = 1) -> Album:
        return Album()

    def fetch_label(self, source: Source, stop_at_level: int = 1) -> Label:
        return Label()

    def download_song_to_target(self, source: Source, target: Target, desc: str = None) -> DownloadResult:
        return DownloadResult()
