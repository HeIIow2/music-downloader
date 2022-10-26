import mutagen.id3
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

# to get all valid keys
from mutagen.easyid3 import EasyID3
print(EasyID3.valid_keys.keys())
"""


def write_metadata(row, file_path):
    # only convert the file to the proper format if mutagen doesn't work with it due to time
    try:
        audiofile = EasyID3(file_path)
    except mutagen.id3.ID3NoHeaderError:
        AudioSegment.from_file(file_path).export(file_path, format="mp3")
        audiofile = EasyID3(file_path)

    valid_keys = list(EasyID3.valid_keys.keys())

    for key in list(row.keys()):
        if type(row[key]) == list or key in valid_keys and not pd.isna(row[key]):
            if type(row[key]) == int or type(row[key]) == float:
                row[key] = str(row[key])
            audiofile[key] = row[key]

    logging.info("saving")
    audiofile.save(file_path, v1=2)


def path_stuff(path: str, file_: str):
    # returns true if it shouldn't be downloaded
    if os.path.exists(file_):
        logging.info(f"'{file_}' does already exist, thus not downloading.")
        return True
    os.makedirs(path, exist_ok=True)
    return False


class Download:
    def __init__(self, proxies: dict = None, file: str = ".cache3.csv", temp: str = "temp",
                 base_path: str = ""):
        if proxies is not None:
            musify.set_proxy(proxies)

        self.temp = temp
        self.file = file

        self.dataframe = pd.read_csv(os.path.join(self.temp, self.file), index_col=0)

        for idx, row in self.dataframe.iterrows():
            row['artist'] = json.loads(row['artist'].replace("'", '"'))
            row['file'] = os.path.join(base_path, row['file'])
            row['path'] = os.path.join(base_path, row['path'])

            if path_stuff(row['path'], row['file']):
                write_metadata(row, row['file'])
                continue

            download_success = None
            src = row['src']
            if src == 'musify':
                download_success = musify.download(row)
            elif src == 'youtube':
                download_success = youtube_music.download(row)

            if download_success == -1:
                logging.warning(f"couldn't download {row.url} from {row.src}")
                continue

            write_metadata(row, row['file'])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = requests.Session()
    Download(session=s, base_path=os.path.expanduser('~/Music'))
