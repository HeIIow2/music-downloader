from ..utils.shared import *

from .sources import (
    youtube,
    musify,
    local_files
)

from ..database.temp_database import temp_database

logger = URL_DOWNLOAD_LOGGER

# maps the classes to get data from to the source name
sources = {
    'Youtube': youtube.Youtube,
    'Musify': musify.Musify
}


class Download:
    def __init__(self) -> None:
        self.urls = []

        for song in temp_database.get_tracks_without_src():

            id_ = song['id']
            if os.path.exists(song.target.file):
                logger.info(f"skipping the fetching of the download links, cuz {song['file']} already exists.")
                continue

            """
            not implemented yet, will in one point crashe everything
            # check File System
            file_path = file_system.get_path(song)
            if file_path is not None:
                self.add_url(file_path, 'file', id_)
                continue
            """
            """
            # check YouTube
            youtube_url = youtube.Youtube.fetch_source(song)
            if youtube_url is not None:
                self.add_url(youtube_url, 'youtube', id_)
                continue

            # check musify
            musify_url = musify.Musify.fetch_source(song)
            if musify_url is not None:
                self.add_url(musify_url, 'musify', id_)
                continue

            # check musify again, but with a different methode that takes longer
            musify_url = musify.get_musify_url_slow(song)
            if musify_url is not None:
                self.add_url(musify_url, 'musify', id_)
                continue
            """
            sucess = False
            for src in AUDIO_SOURCES:
                res = Download.fetch_from_src(song, src)
                if res is not None:
                    sucess = True
                    Download.add_url(res, src, id_)

            if not sucess:
                logger.warning(f"Didn't find any sources for {song}")

    @staticmethod
    def fetch_from_src(song, src):
        if src not in sources:
            raise ValueError(f"source {src} seems to not exist")

        source_subclass = sources[src]
        return source_subclass.fetch_source(song)

    @staticmethod
    def add_url(url: str, src: str, id_: str):
        temp_database.set_download_data(id_, url, src)


if __name__ == "__main__":
    download = Download()
