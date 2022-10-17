import os.path
import shlex
import pandas as pd
import json


class UrlPath:
    def __init__(self, genre: str, temp: str = "temp", file: str = ".cache3.csv", step_two_file: str = ".cache2.csv"):
        self.temp = temp
        self.file = file
        self.metadata = pd.read_csv(os.path.join(self.temp, step_two_file), index_col=0)

        self.genre = genre

        new_metadata = []

        for idx, row in self.metadata.iterrows():
            file, path = self.get_path_from_row(row)
            new_row = dict(row)
            new_row['path'] = path
            new_row['file'] = file
            new_row['genre'] = self.genre
            new_metadata.append(new_row)

        new_df = pd.DataFrame(new_metadata)
        new_df.to_csv(os.path.join(self.temp, self.file))


    def get_path_from_row(self, row):
        """
        genre/artist/song.mp3

        :param row:
        :return: path:
        """
        return os.path.join(self.get_genre(), self.get_artist(row), self.get_album(row), f"{self.get_song(row)}.mp3"), os.path.join(self.get_genre(), self.get_artist(row), self.get_album(row))

    def escape_part(self, part: str):
        return part.replace("/", " ")

    def get_genre(self):
        return self.escape_part(self.genre)

    def get_album(self, row):
        return self.escape_part(row['album'])

    def get_artist(self, row):
        artists = json.loads(row['artist'].replace("'", '"'))
        return self.escape_part(artists[0])

    def get_song(self, row):
        return self.escape_part(row['title'])


if __name__ == "__main__":
    UrlPath("dsbm")
