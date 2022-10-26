import json
import os.path
import pandas as pd
import requests
import logging

import musify
import youtube_music


class Download:
    def __init__(self, metadata_csv: str = ".cache1.csv", proxies: dict = None,
                 file: str = ".cache2.csv", temp: str = "temp") -> None:
        if proxies is not None:
            musify.set_proxy(proxies)

        self.temp = temp
        self.metadata = pd.read_csv(os.path.join(self.temp, metadata_csv), index_col=0)

        self.urls = []

        for idx, row in self.metadata.iterrows():
            row['artist'] = json.loads(row['artist'].replace("'", '"'))

            # check musify
            musify_url = musify.get_musify_url(row)
            if musify_url is not None:
                self.add_url(musify_url, 'musify', dict(row))
                continue

            # check YouTube
            youtube_url = youtube_music.get_youtube_url(row)
            if youtube_url is not None:
                self.add_url(youtube_url, 'youtube', dict(row))
                continue

            # check musify again, but with a different methode that takes longer
            musify_url = musify.get_musify_url_slow(row)
            if musify_url is not None:
                self.add_url(musify_url, 'musify', dict(row))
                continue

            logging.warning(f"Didn't find any sources for {row['title']}")

        self.dump_urls(file)

    def add_url(self, url: str, src: str, row: dict):
        row['url'] = url
        row['src'] = src

        self.urls.append(row)

    def dump_urls(self, file: str = ".cache2.csv"):
        df = pd.DataFrame(self.urls)
        df.to_csv(os.path.join(self.temp, file))


if __name__ == "__main__":
    proxies = {
        'http': 'socks5h://127.0.0.1:9150',
        'https': 'socks5h://127.0.0.1:9150'
    }

    s = requests.Session()
    s.proxies = proxies
    download = Download(session=s)
