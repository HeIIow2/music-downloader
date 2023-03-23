from typing import Optional, List, Tuple
from pathlib import Path
from collections import defaultdict

from ..utils import shared
from .parents import DatabaseObject


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
            _id: str = None,
            dynamic: bool = False,
            relative_to_music_dir: bool = False
    ) -> None:
        super().__init__(_id=_id, dynamic=dynamic)
        self._file: Path = Path(file)
        self._path: Path = Path(path) if relative_to_music_dir else Path(path)

        self.is_relative_to_music_dir: bool = relative_to_music_dir

    @property
    def file_path(self) -> Path:
        return Path(self._path, self._file)

    @property
    def indexing_values(self) -> List[Tuple[str, object]]:
        return [('filepath', self.file_path)]
