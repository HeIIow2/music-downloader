import requests

from .utils.shared import *
from .scraping import musify, youtube_music, file_system

logger = URL_DOWNLOAD_LOGGER


class Download:
    def __init__(self) -> None:
        self.urls = []

        for row in database.get_tracks_without_src():
            row['artists'] = [artist['name'] for artist in row['artists']]

            id_ = row['id']
            if os.path.exists(os.path.join(MUSIC_DIR, row['file'])):
                logger.info(f"skipping the fetching of the download links, cuz {row['file']} already exists.")
                continue

            """
            not implemented yet, will in one point crashe everything
            # check File System
            file_path = file_system.get_path(row)
            if file_path is not None:
                self.add_url(file_path, 'file', id_)
                continue
            """

            # check YouTube
            youtube_url = youtube_music.get_youtube_url(row)
            if youtube_url is not None:
                self.add_url(youtube_url, 'youtube', id_)
                continue

            # check musify
            musify_url = musify.get_musify_url(row)
            if musify_url is not None:
                self.add_url(musify_url, 'musify', id_)
                continue

            # check musify again, but with a different methode that takes longer
            musify_url = musify.get_musify_url_slow(row)
            if musify_url is not None:
                self.add_url(musify_url, 'musify', id_)
                continue

            logger.warning(f"Didn't find any sources for {row['title']}")

    def add_url(self, url: str, src: str, id_: str):
        database.set_download_data(id_, url, src)


if __name__ == "__main__":
    download = Download()
