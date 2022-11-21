import mutagen.id3
import requests
import os.path
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment

from ..utils.shared import *
from .sources import (
    youtube,
    musify,
    local_files
)

logger = DOWNLOAD_LOGGER

# maps the classes to get data from to the source name
sources = {
    'Youtube': youtube.Youtube,
    'Musify': musify.Musify
}

"""
https://en.wikipedia.org/wiki/ID3
https://mutagen.readthedocs.io/en/latest/user/id3.html

# to get all valid keys
from mutagen.easyid3 import EasyID3
print("\n".join(EasyID3.valid_keys.keys()))
print(EasyID3.valid_keys.keys())
"""


class Download:
    def __init__(self):
        for row in database.get_tracks_to_download():
            row['artist'] = [i['name'] for i in row['artists']]
            row['file'] = os.path.join(MUSIC_DIR, row['file'])
            row['path'] = os.path.join(MUSIC_DIR, row['path'])

            if self.path_stuff(row['path'], row['file']):
                self.write_metadata(row, row['file'])
                continue

            # download_success = Download.download_from_src(row['src'], row)
            sources = row['source']
            for source in sources:
                if source['src'] is None:
                    continue
                download_success = Download.download_from_src(source['src'], source['url'], row)
                if download_success != -1:
                    break
                else:
                    logger.warning(f"couldn't download {row['url']} from {row['src']}")

            """
            download_success = None
            src = row['src']
            if src == 'musify':
                download_success = musify.download(row)
            elif src == 'youtube':
                download_success = youtube.download(row)
            """

            self.write_metadata(row, row['file'])

    @staticmethod
    def download_from_src(src, url, row):
        if src not in sources:
            raise ValueError(f"source {src} seems to not exist")
        source_subclass = sources[src]

        return source_subclass.fetch_audio(url, row)

    @staticmethod
    def write_metadata(row, file_path):
        if not os.path.exists(file_path):
            logger.warning(f"file {file_path} doesn't exist")
            return False

        # only convert the file to the proper format if mutagen doesn't work with it due to time
        try:
            audiofile = EasyID3(file_path)
        except mutagen.id3.ID3NoHeaderError:
            AudioSegment.from_file(file_path).export(file_path, format="mp3")
            audiofile = EasyID3(file_path)

        valid_keys = list(EasyID3.valid_keys.keys())

        for key in list(row.keys()):
            if key in valid_keys and row[key] is not None:
                if type(row[key]) != list:
                    row[key] = str(row[key])
                audiofile[key] = row[key]

        logger.info("saving")
        audiofile.save(file_path, v1=2)

    @staticmethod
    def path_stuff(path: str, file_: str):
        # returns true if it shouldn't be downloaded
        if os.path.exists(file_):
            logger.info(f"'{file_}' does already exist, thus not downloading.")
            return True
        os.makedirs(path, exist_ok=True)
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = requests.Session()
    Download()
