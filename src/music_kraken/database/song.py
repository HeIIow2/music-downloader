from typing import List
from ..utils.shared import (
    MUSIC_DIR
)

import os
from mutagen.easyid3 import EasyID3


class Target:
    def __init__(self) -> None:
        self._file = None
        self._path = None

    def set_file(self, _file: str):
        self._file = _file

    def get_file(self) -> str | None:
        if self._file is None:
            return None
        return os.path.join(MUSIC_DIR, self._file)

    def set_path(self, _path: str):
        self._path = _path

    def get_path(self) -> str | None:
        if self._path is None:
            return None
        return os.path.join(MUSIC_DIR, self._path)

    file = property(fget=get_file, fset=set_file)
    path = property(fget=get_path, fset=set_path)


class Artist:
    def __init__(self, artist_data) -> None:
        self.artist_data = artist_data

        self.id = self.artist_data['id']
        self.name = self.artist_data['name']

    def __eq__(self, __o: object) -> bool:
        if type(__o) != type(self):
            return False
        return self.id == __o.id

    def __str__(self) -> str:
        return self.name


class Source:
    def __init__(self, src_data) -> None:
        self.src_data = src_data

        self.src = self.src_data['src']
        self.url = self.src_data['url']


class Metadata:
    def __init__(self) -> None:
        self.data = {}

    def get_all_metadata(self):
        return list(self.data.items())

    def __setitem__(self, item, value):
        if item in EasyID3.valid_keys.keys():
            self.data[item] = value

    def __getitem__(self, item):
        if item not in self.data:
            return None
        return self.data[item]


class Song:
    def __init__(self, json_response) -> None:
        self.json_data = json_response

        # initialize the data
        self.title = self.json_data['title']
        self.artists = []
        for a in self.json_data['artists']:
            new_artist = Artist(a)
            exists = False
            for existing_artist in self.artists:
                if new_artist == existing_artist:
                    exists = True
                    break
            if not exists:
                self.artists.append(new_artist)
        self.isrc = self.json_data['isrc']

        # initialize the sources
        self.sources: List[Source] = []
        for src in self.json_data['source']:
            if src['src'] is None:
                continue
            self.sources.append(Source(src))

        # initialize the target
        self.target = Target()
        self.target.file = self.json_data['file']
        self.target.path = self.json_data['path']

        # initialize id3 metadata
        self.metadata = Metadata()
        for key, value in self.json_data.items():
            self.metadata[key] = value
        self.metadata['artist'] = self.get_artist_names()
        # EasyID3.valid_keys.keys()

    def __str__(self) -> str:
        return f"\"{self.title}\" by {', '.join([str(a) for a in self.artists])}"

    def get_metadata(self):
        return self.metadata.get_all_metadata()

    def has_isrc(self) -> bool:
        return self.isrc is not None

    def get_artist_names(self) -> List[str]:
        return [a.name for a in self.artists]

    def __getitem__(self, item):
        if item not in self.json_data:
            return None
        return self.json_data[item]

    def __setitem__(self, item, value):
        if item == "file":
            self.target.file = value
            return
        if item == "path":
            self.target.path = value
            return

        self.json_data[item] = value
