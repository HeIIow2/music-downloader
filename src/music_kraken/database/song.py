from typing import List
from ..utils.shared import *

import os

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
        self.artist_data

        self.id = self.artist_data['id']
        self.name = self.artist_data['name']

class Source:
    def __init__(self, src_data) -> None:
        self.src_data = src_data

        self.src = self.src_data['src']
        self.url = self.src_data['url']


class Song:
    def __init__(self, json_response) -> None:
        self.json_data = json_response

        # initialize the data
        self.title = self.json_data['title']
        self.artists = [Artist(a) for a in self.json_data['artists']]
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

    def has_isrc(self) -> bool:
        return self.isrc is not None

    def get_artist_names(self) -> List[str]:
        return [a.name for a in self.aritsts]

    def __getitem__(self, item):
        print(item)
        print(self.json_data)
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
        print(item, value)
        self.json_data[item] = value
