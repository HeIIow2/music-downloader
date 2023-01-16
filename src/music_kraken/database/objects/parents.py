import uuid

from ...utils.shared import (
    SONG_LOGGER as logger
)


class Reference:
    def __init__(self, id_: str) -> None:
        self.id = id_

    def __str__(self):
        return f"references to an object with the id: {self.id}"

    def __eq__(self, __o: object) -> bool:
        if type(__o) != type(self):
            return False
        return self.id == __o.id


class DatabaseObject:
    def __init__(self, id_: str = None, dynamic: bool = False) -> None:
        self.id_: str | None = id_
        self.dynamic = dynamic

    def get_id(self) -> str:
        """
        returns the id if it is set, else
        it returns a randomly generated UUID
        https://docs.python.org/3/library/uuid.html

        if the object is dynamic, it raises an error
        """
        if self.dynamic:
            raise ValueError("Dynamic objects have no idea, because they are not in the database")

        if self.id_ is None:
            self.id_ = str(uuid.uuid4())
            logger.info(f"id for {self.__str__()} isn't set. Setting to {self.id_}")

        return self.id_

    def get_reference(self) -> Reference:
        return Reference(self.id)

    id = property(fget=get_id)
    reference = property(fget=get_reference)


class SongAttribute:
    def __init__(self, song=None):
        # the reference to the song the lyrics belong to
        self.song = song

    def add_song(self, song):
        self.song = song

    def get_ref_song_id(self):
        if self.song is None:
            return None
        return self.song.reference.id

    def set_ref_song_id(self, song_id):
        self.song_ref = Reference(song_id)

    song_ref_id = property(fget=get_ref_song_id, fset=set_ref_song_id)


class ID3Metadata:
    def get_metadata(self):
        pass

    def get_id3_dict(self) -> dict:
        return {}

    id3_dict: dict = property(fget=get_id3_dict)
