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
from ..database import song as song_objects
from ..database.temp_database import temp_database

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
        for song in temp_database.get_tracks_to_download():

            if self.path_stuff(song.target):
                self.write_metadata(song)
                continue

            # download_success = Download.download_from_src(song['src'], song)
            for source in song.sources:
                download_success = Download.download_from_src(song, source)
                if download_success != -1:
                    break
                else:
                    logger.warning(f"couldn't download {song['url']} from {song['src']}")

            """
            download_success = None
            src = song['src']
            if src == 'musify':
                download_success = musify.download(song)
            elif src == 'youtube':
                download_success = youtube.download(song)
            """

            self.write_metadata(song)

    @staticmethod
    def download_from_src(song, src):
        if src.src not in sources:
            raise ValueError(f"source {src.src} seems to not exist")
        source_subclass = sources[src.src]

        return source_subclass.fetch_audio(song, src)

    @staticmethod
    def write_metadata(song: song_objects.Song):
        if not os.path.exists(song.target.file):
            logger.warning(f"file {song.target.file} doesn't exist")
            return False

        # only convert the file to the proper format if mutagen doesn't work with it due to time
        try:
            audiofile = EasyID3(song.target.file)
        except mutagen.id3.ID3NoHeaderError:
            AudioSegment.from_file(song.target.file).export(song.target.file, format="mp3")
            audiofile = EasyID3(song.target.file)

        for key, value in song.get_metadata():
            if type(value) != list:
                value = str(value)
            audiofile[key] = value

        logger.info("saving")
        audiofile.save(song.target.file, v1=2)

    @staticmethod
    def path_stuff(target: song_objects.Target) -> bool:
        # returns true if it shouldn't be downloaded
        if os.path.exists(target.file):
            logger.info(f"'{target.file}' does already exist, thus not downloading.")
            return True
        os.makedirs(target.path, exist_ok=True)
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = requests.Session()
    Download()
