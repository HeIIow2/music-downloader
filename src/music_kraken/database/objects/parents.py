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
    empty: bool

    def __init__(self, id_: str = None, dynamic: bool = False, empty: bool = False, **kwargs) -> None:
        """
        empty means it is an placeholder.
        it makes the object perform the same, it is just the same
        """
        self.id_: str | None = id_
        self.dynamic = dynamic
        self.empty = empty

    def get_id(self) -> str:
        """
        returns the id if it is set, else
        it returns a randomly generated UUID
        https://docs.python.org/3/library/uuid.html

        if the object is empty, it returns None
        if the object is dynamic, it raises an error
        """
        if self.empty:
            return None
        if self.dynamic:
            raise ValueError("Dynamic objects have no idea, because they are not in the database")

        if self.id_ is None:
            self.id_ = str(uuid.uuid4())
            logger.info(f"id for {self.__str__()} isn't set. Setting to {self.id_}")

        return self.id_

    def get_reference(self) -> Reference:
        return Reference(self.id)

    def get_options(self) -> list:
        """
        makes only sense in
         - artist
         - song
         - album
        """
        return []

    def get_option_string(self) -> str:
        """
        makes only sense in
         - artist
         - song
         - album
        """
        return ""

    id = property(fget=get_id)
    reference = property(fget=get_reference)
    options = property(fget=get_options)
    options_str = property(fget=get_option_string)


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
