import os.path
import logging

from .utils.shared import *

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

        for row in database.get_tracks_without_filepath():
            file, path = self.get_path_from_row(row)
            database.set_filepath(row['id'], file, path, genre)

    def get_path_from_row(self, row):
        """
        genre/artist/song.mp3

        :param row:
        :return: path:
        """
        return os.path.join(self.get_genre(), self.get_artist(row), self.get_album(row),
                            f"{self.get_song(row)}.mp3"), os.path.join(self.get_genre(), self.get_artist(row),
                                                                       self.get_album(row))

    @staticmethod
    def escape_part(part: str):
        return unhide(part.replace("/", " "))

    def get_genre(self):
        return self.escape_part(self.genre)

    def get_album(self, row):
        return self.escape_part(row['album'])

    def get_artist(self, row):
        artists = [artist['name'] for artist in row['artists']]
        return self.escape_part(artists[0])

    def get_song(self, row):
        return self.escape_part(row['title'])


if __name__ == "__main__":
    UrlPath("dsbm")
