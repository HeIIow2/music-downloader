import mutagen 
from mutagen.id3 import ID3, Frame

from typing import List
import logging

from ..utils.shared import (
    TAGGING_LOGGER as logger
)
from ..database import (
    Song
)


class AudioMetadata:
    def __init__(self, file_location: str = None) -> None:
        self._file_location = None

        self.frames: ID3 = ID3()

        if file_location is not None:
            self.file_location = file_location


    def add_song_metadata(self, song: Song):
        print("adding")
        for key, value in song.metadata:
            """
            https://www.programcreek.com/python/example/84797/mutagen.id3.ID3
            """
            print(key, value)
            self.frames.add(mutagen.id3.Frames[key](encoding=3, text=value))

    def save(self, file_location: str = None):
        if file_location is not None:
            self.file_location = file_location

        if self.file_location is None:
            raise Exception("no file target provided to save the data to")
        self.frames.save(self.file_location, v2_version=4)

    def set_file_location(self, file_location):
        # try loading the data from the given file. if it doesn't succeed the frame remains empty
        try:
            self.frames.load(file_location, v2_version=4)
            self._file_location = file_location
        except mutagen.MutagenError:
            logger.warning(f"couldn't find any metadata at: \"{self.file_location}\"")

    file_location = property(fget=lambda self: self._file_location, fset=set_file_location)


def write_metadata(song: Song):
    if not song.target.exists_on_disc:
        print(song.target.file)
        return
    
    id3_object = AudioMetadata(file_location=song.target.file)
    id3_object.add_song_metadata(song=song)
    id3_object.save()


def write_many_metadata(song_list: List[Song]):
    for song in song_list:
        write_metadata(song=song)


if __name__ == "__main__":
    print("called directly")
    filepath = "/home/lars/Music/deathcore/Archspire/Bleed the Future/Bleed the Future.mp3"

    audio_metadata = AudioMetadata(file_location=filepath)
    print(audio_metadata.frames.pprint())
