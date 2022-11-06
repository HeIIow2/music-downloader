import requests
import logging

import musify
import youtube_music


class Download:
    def __init__(self, database, logger: logging.Logger, proxies: dict = None) -> None:
        self.database = database
        self.logger = logger
        if proxies is not None:
            musify.set_proxy(proxies)

        self.urls = []

        for row in self.database.get_tracks_to_download():
            row['artists'] = [artist['name'] for artist in row['artists']]

            id_ = row['id']

            # check musify
            musify_url = musify.get_musify_url(row)
            if musify_url is not None:
                self.add_url(musify_url, 'musify', id_)
                continue

            # check YouTube
            youtube_url = youtube_music.get_youtube_url(row)
            if youtube_url is not None:
                self.add_url(youtube_url, 'youtube', id_)
                continue

            # check musify again, but with a different methode that takes longer
            musify_url = musify.get_musify_url_slow(row)
            if musify_url is not None:
                self.add_url(musify_url, 'musify', id_)
                continue

            self.logger.warning(f"Didn't find any sources for {row['title']}")

    def add_url(self, url: str, src: str, id_: str):
        self.database.set_download_data(id_, url, src)


if __name__ == "__main__":
    proxies = {
        'http': 'socks5h://127.0.0.1:9150',
        'https': 'socks5h://127.0.0.1:9150'
    }

    s = requests.Session()
    s.proxies = proxies
    download = Download()
