import requests
import os.path
import pandas as pd

import logging


class Download:
    def __init__(self, session: requests.Session = requests.Session(), file: str = ".cache3.csv", temp: str = "temp"):
        self.session = session
        self.session.headers = {
            "Connection": "keep-alive",
            "Referer": "https://musify.club/"
        }
        self.temp = temp
        self.file = file

        self.dataframe = pd.read_csv(os.path.join(self.temp, self.file), index_col=0)

        for idx, row in self.dataframe.iterrows():
            self.download(row['path'], row['file'], row['url'])

    def download(self, path, file, url):
        if os.path.exists(file):
            return
        os.makedirs(path, exist_ok=True)

        logging.info(f"downloading: {url}")
        r = self.session.get(url)
        if r.status_code != 200:
            if r.status_code == 404:
                logging.warning(f"{url} was not found")
                return -1
            raise ConnectionError(f"\"{url}\" returned {r.status_code}: {r.text}")
        with open(file, "wb") as mp3_file:
            mp3_file.write(r.content)
        logging.info("finished")


"""
class Track:
    def __init__(self, url: str, release: Release, track_name: str, track_artists: list = None,
                 session: requests.Session = requests.Session()):
        self.session = session
        self.url = url

        parsed_url = urllib.parse.urlparse(url)
        path = os.path.normpath(parsed_url.path)
        split_path = path.split(os.sep)

        url_type = split_path[1]
        if url_type != "track":
            raise Exception(f'"{url}" is supposed to link a track.')
        name = split_path[2]
        name = name.split("-")

        self.id = name[-1]
        self.name = "-".join(name[:-1])

        self.track_artists = track_artists
        self.release = release
        self.pretty_track = track_name
        self.mp3_url = self.get_mp3_url()

    def __str__(self):

    def fetch(self):
        return

    def get_mp3_url(self):
        # https://musify.club/track/dl/17254894/ghost-bath-convince-me-to-bleed.mp3
        return f"https://musify.club/track/dl/{self.id}/{self.name}.mp3"

    def add_album_art(self, path):


        img = self.release.raw_artwork

        audio = EasyMP3(path, ID3=ID3)

        try:
            audio.add_tags()
        except _util.error:
            pass

        audio.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime='image/png',
                type=3,  # 3 is for album art
                desc='Cover',
                data=img.read()  # Reads and adds album art
            )
        )
        audio.save()

    def download(self):
        download_path = os.path.join(self.release.path, self.name + ".mp3")
        # download only when the file doesn't exist yet
        if not os.path.exists(download_path):
            logging.info(f"downloading: {self.mp3_url}")
            r = requests.get(self.mp3_url, proxies=proxy)
            if r.status_code != 200:
                if r.status_code == 404:
                    logging.warning(f"{self.mp3_url} was not found")
                    return -1
                raise ConnectionError(f"\"{self.mp3_url}\" returned {r.status_code}: {r.text}")
            with open(download_path, "wb") as mp3_file:
                mp3_file.write(r.content)
            logging.info("finished")

        audiofile = EasyID3(download_path)
        if self.track_artists is not None:
            audiofile["artist"] = self.track_artists
        else:
            audiofile["artist"] = self.release.pretty_release
        audiofile["albumartist"] = self.release.artist.pretty_name
        audiofile["date"] = self.release.year

        if self.release.genre is not None:
            audiofile["genre"] = self.release.genre

        audiofile["title"] = self.pretty_track
        audiofile["album"] = self.release.pretty_release

        audiofile.save()
        # self.add_album_art(download_path)

"""

if __name__ == "__main__":
    proxies = {
        'http': 'socks5h://127.0.0.1:9150',
        'https': 'socks5h://127.0.0.1:9150'
    }

    s = requests.Session()
    s.proxies = proxies
    Download(session=s)
