import os

from ..utils.shared import (
    MUSIC_DIR
)


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
