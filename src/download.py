import requests
import os.path
import pandas as pd
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment
import json
import logging

import musify
import youtube_music

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
            if self.path_stuff(row['path'], row['file']):
                self.write_metadata(row, row['file'])
                continue

            src = row['src']
            if src == 'musify':
                musify.download(row)
            elif src == 'youtube':
                youtube_music.download(row)
            self.write_metadata(row, row['file'])

    def path_stuff(self, path: str, file_: str):
        # returns true if it shouldn't be downloaded
        if os.path.exists(file_):
            logging.info(f"'{file_}' does already exist, thus not downloading.")
            return True
        os.makedirs(path, exist_ok=True)
        return False

    def write_metadata(self, row, filePath):
        AudioSegment.from_file(filePath).export(filePath, format="mp3")
        
        audiofile = EasyID3(filePath)
        
        valid_keys = list(EasyID3.valid_keys.keys())

        for key in list(row.keys()):
            if key in valid_keys and row[key] is not None and not pd.isna(row[key]):
                # print(key)
                if type(row[key]) == int or type(row[key]) == float:
                    row[key] = str(row[key])
                audiofile[key] = row[key]

        print("saving")
        audiofile.save(filePath, v1=2)



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = requests.Session()
    Download(session=s)
