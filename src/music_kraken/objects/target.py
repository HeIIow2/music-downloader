from pathlib import Path
from typing import List, Tuple, TextIO
import logging

import requests
from tqdm import tqdm

from .parents import DatabaseObject
from ..utils.config import main_settings, logging_settings
from ..utils.string_processing import fit_to_file_system


LOGGER = logging.getLogger("target")


class Target(DatabaseObject):
    """
    create somehow like that
    ```python
    # I know path is pointless, and I will change that (don't worry about backwards compatibility there)
    Target(file="song.mp3", path="~/Music/genre/artist/album")
    ```
    """

    SIMPLE_STRING_ATTRIBUTES = {
        "_file": None,
        "_path": None
    }
    COLLECTION_STRING_ATTRIBUTES = tuple()

    def __init__(
            self,
            file: str = None,
            path: str = None,
            dynamic: bool = False,
            relative_to_music_dir: bool = False
    ) -> None:
        super().__init__(dynamic=dynamic)
        self._file: Path = Path(fit_to_file_system(file))
        self._path: Path = fit_to_file_system(Path(main_settings["music_directory"], path) if relative_to_music_dir else Path(path))

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
            LOGGER.warning(f"No file exists at: {self.file_path}")
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

                    for chunk in r.iter_content(chunk_size=main_settings["chunk_size"]):
                        size = f.write(chunk)
                        t.update(size)
                return True

            except requests.exceptions.Timeout:
                logging_settings["download_logger"].error("Stream timed out.")
                return False

    def open(self, file_mode: str, **kwargs) -> TextIO:
        return self.file_path.open(file_mode, **kwargs)
            
    def delete(self):
        self.file_path.unlink(missing_ok=True)
