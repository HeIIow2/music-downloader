from typing import List

from .artist import Artist
from .metadata import Metadata
from .source import Source
from .target import Target


class Song:
    def __init__(self, json_response) -> None:
        self.json_data = json_response

        # initialize the data
        self.id = self.json_data['id']
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
