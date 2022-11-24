from typing import List

from ..utils.shared import *
from .sources import (
    youtube,
    musify,
    local_files
)
from ..database.song import Song as song_object
from ..database.temp_database import temp_database

logger = URL_DOWNLOAD_LOGGER

# maps the classes to get data from to the source name
sources = {
    'Youtube': youtube.Youtube,
    'Musify': musify.Musify
}


class Download:
    def __init__(self) -> None:
        for song in temp_database.get_tracks_without_src():
            id_ = song['id']
            if os.path.exists(song.target.file):
                logger.info(f"skipping the fetching of the download links, cuz {song.target.file} already exists.")
                continue

            sucess = False
            for src in AUDIO_SOURCES:
                res = Download.fetch_from_src(song, src)
                if res is not None:
                    sucess = True
                    Download.add_url(res, src, id_)

            if not sucess:
                logger.warning(f"Didn't find any sources for {song}")

    @classmethod
    def fetch_sources(cls, songs: List[song_object], skip_existing_files: bool = False):
        for song in songs:
            if os.path.exists(song.target.file) and skip_existing_files:
                logger.info(f"skipping the fetching of the download links, cuz {song.target.file} already exists.")
                continue

            sucess = False
            for src in AUDIO_SOURCES:
                res = cls.fetch_from_src(song, src)
                if res is not None:
                    sucess = True
                    cls.add_url(res, src, song.id)

            if not sucess:
                logger.warning(f"Didn't find any sources for {song}")
    

    @classmethod
    def fetch_from_src(cls, song, src):
        if src not in sources:
            raise ValueError(f"source {src} seems to not exist")

        source_subclass = sources[src]
        return source_subclass.fetch_source(song)

    @classmethod
    def add_url(cls, url: str, src: str, id_: str):
        temp_database.set_download_data(id_, url, src)


if __name__ == "__main__":
    download = Download()
