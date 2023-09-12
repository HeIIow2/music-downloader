from typing import List, Optional, Type
from urllib.parse import urlparse
import json
from enum import Enum
from bs4 import BeautifulSoup

from ..objects import Source, DatabaseObject
from .abstract import Page
from ..objects import (
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    Label,
    Target,
    Contact
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
    HOST = "https://onlysmile.bandcamp.com"

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
    

    def fetch_label(self, source: Source, stop_at_level: int = 1) -> Label:
        return Label()

    def _parse_artist_details(self, soup: BeautifulSoup) -> Artist:
        name: str = None
        source_list: List[Source] = []
        contact_list: List[Contact] = []
        
        band_name_location: BeautifulSoup = soup.find("p", {"id": "band-name-location"})
        if band_name_location is not None:
            title_span = band_name_location.find("span", {"class": "title"})
            if title_span is not None:
                name = title_span.text.strip()
        
        link_container: BeautifulSoup = soup.find("ol", {"id": "band-links"})
        if link_container is not None:
            li: BeautifulSoup
            for li in link_container.find_all("a"):
                if li is None and li['href'] is not None:
                    continue

                source_list.append(Source.match_url(li['href'], referer_page=self.SOURCE_TYPE))

        return Artist(
            name=name,
            source_list=source_list
        )
    
    def _parse_song_list(self, soup: BeautifulSoup) -> List[Album]:
        title = None
        source_list: List[Source] = []

        a = soup.find("a")
        if a is not None and a["href"] is not None:
            source_list.append(Source(self.SOURCE_TYPE, self.HOST + a["href"]))
        
        title_p = soup.find("p", {"class": "title"})
        if title_p is not None:
            title = title_p.text.strip()

        return Album(title=title, source_list=source_list)

    def fetch_artist(self, source: Source, stop_at_level: int = 1) -> Artist:
        artist = Artist()

        r = self.connection.get(source.url)
        if r is None:
            return artist
        
        soup = self.get_soup_from_response(r)

        if DEBUG:
            dump_to_file("artist_page.html", r.text, exit_after_dump=False)

        artist = self._parse_artist_details(soup=soup.find("div", {"id": "bio-container"}))
        for subsoup in soup.find("ol", {"id": "music-grid"}).find_all("li"):
            artist.main_album_collection.append(self._parse_song_list(soup=subsoup))

        return artist
    
    def _parse_track_element(self, track: dict) -> Optional[Song]:
        return Song(
            title=track["item"]["name"],
            source_list=[Source(self.SOURCE_TYPE, track["item"]["mainEntityOfPage"])],
            tracksort=track["position"]
        )

    def fetch_album(self, source: Source, stop_at_level: int = 1) -> Album:
        print(source)
        album = Album()

        r = self.connection.get(source.url)
        if r is None:
            return album
        
        soup = self.get_soup_from_response(r)

        if DEBUG:
            # dump_to_file("album_page.html", r.text, exit_after_dump=False)
            pass

        data_container = soup.find("script", {"type": "application/ld+json"})
        
        if DEBUG:
            dump_to_file("album_data.json", data_container.text, is_json=True, exit_after_dump=False)

        data = json.loads(data_container.text)

        for i, track_json in enumerate(data.get("track", {}).get("itemListElement", [])):
            if DEBUG:
                dump_to_file(f"album_track_{i}.json", json.dumps(track_json), is_json=True, exit_after_dump=False)

            try:
                album.song_collection.append(self._parse_track_element(track_json))
            except KeyError:
                continue

        return album

    def fetch_song(self, source: Source, stop_at_level: int = 1) -> Song:
        print(source)
        return Song()

    def download_song_to_target(self, source: Source, target: Target, desc: str = None) -> DownloadResult:
        return DownloadResult()
