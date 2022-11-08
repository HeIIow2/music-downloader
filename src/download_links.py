import requests
import os
import logging

from scraping import musify, youtube_music


class Download:
<<<<<<< HEAD
    def __init__(self, metadata_csv: str = ".cache1.csv", session: requests.Session = requests.Session(),
                 file: str = ".cache2.csv", temp: str = "temp") -> None:
        self.temp = temp
        self.metadata = pd.read_csv(os.path.join(self.temp, metadata_csv), index_col=0)
=======
    def __init__(self, database, logger: logging.Logger, music_dir: str, proxies: dict = None) -> None:
        self.music_dir = music_dir
        self.database = database
        self.logger = logger
        if proxies is not None:
            musify.set_proxy(proxies)
>>>>>>> 63f30bffbae20ec3fc368a6093b28e56f0230318

        self.urls = []

        for row in self.database.get_tracks_without_src():
            row['artists'] = [artist['name'] for artist in row['artists']]

            id_ = row['id']
            if os.path.exists(os.path.join(self.music_dir, row['file'])):
                self.logger.info(f"skipping the fetching of the download links, cuz {row['file']} already exists.")
                continue

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
