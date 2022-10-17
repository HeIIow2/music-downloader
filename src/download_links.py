import os.path

import pandas as pd
import requests


# https://musify.club/search/suggestions?term=happy days

class Download:
    def __init__(self, metadata_csv: str = ".cache1.csv", session: requests.Session = requests.Session(),
                 file: str = ".cache2.csv", temp: str = "temp") -> None:
        self.temp = temp

        self.session = session
        self.session.headers = {
            "Connection": "keep-alive",
            "Referer": "https://musify.club/"
        }

        self.metadata = pd.read_csv(os.path.join(self.temp, metadata_csv), index_col=0)

        self.urls = []
        missing_urls, self.urls = self.check_musify()

        self.dump_urls(file)

    def check_musify_track(self, row):
        artist = row['artist']
        track = row['title']

        url = f"https://musify.club/search/suggestions?term={track}"

        r = self.session.get(url=url)
        if r.status_code == 200:
            autocomplete = r.json()
            for row in autocomplete:
                if any(a in row['label'] for a in artist):
                    return row

        return None

    def check_musify(self, urls: list = []):
        missing_urls = []

        def get_download_link(default_url):
            # https://musify.club/track/dl/18567672/rauw-alejandro-te-felicito-feat-shakira.mp3
            # /track/sundenklang-wenn-mein-herz-schreit-3883217'

            file_ = default_url.split("/")[-1]
            musify_id = file_.split("-")[-1]
            musify_name = "-".join(file_.split("-")[:-1])

            return f"https://musify.club/track/dl/{musify_id}/{musify_name}.mp3"

        for idx, row in self.metadata.iterrows():
            url = self.check_musify_track(row)
            if url is None:
                missing_urls.append(row['id'])
                continue
            data = dict(row)
            data['url'] = get_download_link(url['url'])
            urls.append(data)

        return missing_urls, urls

    def dump_urls(self, file: str = ".cache2.csv"):
        df = pd.DataFrame(self.urls)
        df.to_csv(os.path.join(self.temp, file))


if __name__ == "__main__":
    download = Download()
