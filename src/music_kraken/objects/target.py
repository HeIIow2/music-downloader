from pathlib import Path
from typing import List, Tuple

import requests
from tqdm import tqdm

from .parents import DatabaseObject
from ..utils import shared


class Target(DatabaseObject):
    """
    create somehow like that
    ```python
    # I know path is pointless, and I will change that (don't worry about backwards compatibility there)
    Target(file="song.mp3", path="~/Music/genre/artist/album")
    ```
    """

    SIMPLE_ATTRIBUTES = {
        "_file": None,
        "_path": None
    }
    COLLECTION_ATTRIBUTES = tuple()

    def __init__(
            self,
            file: str = None,
            path: str = None,
            dynamic: bool = False,
            relative_to_music_dir: bool = False
    ) -> None:
        super().__init__(dynamic=dynamic)
        self._file: Path = Path(file)
        self._path: Path = Path(shared.MUSIC_DIR, path) if relative_to_music_dir else Path(path)

        self.is_relative_to_music_dir: bool = relative_to_music_dir

    def __repr__(self) -> str:
        return str(self.file_path)

    @property
    def file_path(self) -> Path:
        return Path(self._path, self._file)

    @property
    def indexing_values(self) -> List[Tuple[str, object]]:
        return [('filepath', self.file_path)]

    @property
    def exists(self) -> bool:
        return self.file_path.is_file()
    
    @property
    def size(self) -> int:
        """
        returns the size the downloaded autio takes up in bytes
        returns 0 if the file doesn't exsit
        """
        if not self.exists:
            return 0
        
        return self.file_path.stat().st_size

    def create_path(self):
        self._path.mkdir(parents=True, exist_ok=True)

    def copy_content(self, copy_to: "Target"):
        if not self.exists:
            return

        with open(self.file_path, "rb") as read_from:
            copy_to.create_path()
            with open(copy_to.file_path, "wb") as write_to:
                write_to.write(read_from.read())

    def stream_into(self, r: requests.Response, desc: str = None) -> bool:
        if r is None:
            return False

        self.create_path()

        total_size = int(r.headers.get('content-length'))

        with open(self.file_path, 'wb') as f:
            try:
                """
                https://en.wikipedia.org/wiki/Kilobyte
                > The internationally recommended unit symbol for the kilobyte is kB.
                """
                with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc=desc) as t:

                    for chunk in r.iter_content(chunk_size=shared.CHUNK_SIZE):
                        size = f.write(chunk)
                        t.update(size)
                return True

            except requests.exceptions.Timeout:
                shared.DOWNLOAD_LOGGER.error("Stream timed out.")
                return False
