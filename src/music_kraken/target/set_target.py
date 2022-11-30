import os.path
import logging

from ..utils.shared import *
from ..database.temp_database import temp_database

logger = PATH_LOGGER

UNHIDE_CHAR = '_'

def unhide(part: str):
    if len(part) == 0:
        return ""
    if part[0] == ".":
        return part.replace(".", UNHIDE_CHAR, 1)
    
    return part


class UrlPath:
    def __init__(self, genre: str):

        self.genre = genre

        for song in temp_database.get_tracks_without_filepath():
            # print(song)
            file, path = self.get_path_from_song(song)
            logger.info(f"setting target to {file}")
            temp_database.set_filepath(song.id, file, path, genre)

    def get_path_from_song(self, song):
        """
        genre/artist/song.mp3

        :param song:
        :return: path:
        """
        return os.path.join(self.get_genre(), self.get_artist(song), self.get_album(song),
                            f"{self.get_song(song)}.mp3"), os.path.join(self.get_genre(), self.get_artist(song),
                                                                       self.get_album(song))

    @staticmethod
    def escape_part(part: str):
        return unhide(part.replace("/", " "))

    def get_genre(self):
        return self.escape_part(self.genre)

    def get_album(self, song):
        return self.escape_part(song.release)

    def get_artist(self, song):
        artists = song.get_artist_names()
        return self.escape_part(artists[0])

    def get_song(self, song):
        return self.escape_part(song.title)


if __name__ == "__main__":
    UrlPath("dsbm")
