import requests
import os.path
import pandas as pd
from mutagen.easyid3 import EasyID3
import json

import logging

"""
https://en.wikipedia.org/wiki/ID3
https://mutagen.readthedocs.io/en/latest/user/id3.html

>>> from mutagen.easyid3 import EasyID3
>>> print(EasyID3.valid_keys.keys())
dict_keys(
    [
        'album',
        'bpm',
        'compilation',
        'composer',
        'copyright',
        'encodedby',
        'lyricist',
        'length',
        'media',
        'mood',
        'grouping',
        'title',
        'version',
        'artist',
        'albumartist',
        'conductor',
        'arranger',
        'discnumber',
        'organization',
        'tracknumber',
        'author',
        'albumartistsort',
        'albumsort',
        'composersort',
        'artistsort',
        'titlesort',
        'isrc',
        'discsubtitle',
        'language',
        'genre',
        'date',
        'originaldate',
        'performer:*',
        'musicbrainz_trackid',
        'website',
        'replaygain_*_gain',
        'replaygain_*_peak',
        'musicbrainz_artistid',
        'musicbrainz_albumid',
        'musicbrainz_albumartistid',
        'musicbrainz_trmid',
        'musicip_puid',
        'musicip_fingerprint',
        'musicbrainz_albumstatus',
        'musicbrainz_albumtype', <----------
        'releasecountry',
        'musicbrainz_discid',
        'asin',
        'performer',
        'barcode',
        'catalognumber',
        'musicbrainz_releasetrackid',
        'musicbrainz_releasegroupid',
        'musicbrainz_workid',
        'acoustid_fingerprint',
        'acoustid_id'
        ])
"""

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
            row['artist'] = json.loads(row['artist'].replace("'", '"'))
            self.download(row['path'], row['file'], row['url'])
            self.write_metadata(row, row['file'])

    def download(self, path, file, url):
        if os.path.exists(file):
            logging.info(f"'{file}' does already exist, thus not downloading.")
            return
        os.makedirs(path, exist_ok=True)

        logging.info(f"downloading: '{url}'")
        r = self.session.get(url)
        if r.status_code != 200:
            if r.status_code == 404:
                logging.warning(f"{url} was not found")
                return -1
            raise ConnectionError(f"\"{url}\" returned {r.status_code}: {r.text}")
        with open(file, "wb") as mp3_file:
            mp3_file.write(r.content)
        logging.info("finished")

    def write_metadata(self, row, file):
        audiofile = EasyID3(file)
        
        valid_keys = list(EasyID3.valid_keys.keys())

        for key in list(row.keys()):
            if key in valid_keys and row[key] is not None and not pd.isna(row[key]):
                if type(row[key]) == int or type(row[key]) == float:
                    row[key] = str(row[key])
                audiofile[key] = row[key]

        """
        audiofile["artist"] = row['artist']
        audiofile["albumartist"] = row['album_artist']
        audiofile["date"] = str(row['year'])
        audiofile["genre"] = row['genre']
        audiofile["title"] = row['title']
        audiofile["album"] = row['album']
        audiofile["tracknumber"] = str(row['track'])
        """

        audiofile.save()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = requests.Session()
    if False:
        proxies = {
            'http': 'socks5h://127.0.0.1:9150',
            'https': 'socks5h://127.0.0.1:9150'
        }
        s.proxies = proxies
    Download(session=s)
