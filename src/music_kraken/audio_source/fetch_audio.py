from typing import List
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
from ..database.song import (
    Song as song_object,
    Target as target_object,
    Source as source_object
)
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
        Download.fetch_audios(temp_database.get_tracks_to_download())

    @classmethod
    def fetch_audios(cls, songs: List[song_object], override_existing: bool = False):
        for song in songs:
            if not cls.path_stuff(song.target) and not override_existing:
                cls.write_metadata(song)
                continue

            is_downloaded = False
            for source in song.sources:
                download_success = Download.download_from_src(song, source)

                if download_success == -1:
                    logger.warning(f"couldn't download {song['url']} from {song['src']}")
                else:
                    is_downloaded = True
                    break

            if is_downloaded:
                cls.write_metadata(song)

    @classmethod
    def download_from_src(cls, song: song_object, source: source_object):
        if source.src not in sources:
            raise ValueError(f"source {source.src} seems to not exist")
        source_subclass = sources[source.src]

        return source_subclass.fetch_audio(song, source)

    @classmethod
    def write_metadata(cls, song: song_object):
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

    @classmethod
    def path_stuff(cls, target: target_object) -> bool:
        # returns true if it should be downloaded
        if os.path.exists(target.file):
            logger.info(f"'{target.file}' does already exist, thus not downloading.")
            return False
        os.makedirs(target.path, exist_ok=True)
        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = requests.Session()
    Download()
