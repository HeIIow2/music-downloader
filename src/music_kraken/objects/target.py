from typing import Optional, List, Tuple
from pathlib import Path
from collections import defaultdict
import requests
# from tqdm import tqdm

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
    
    def create_path(self):
        self._path.mkdir(parents=True, exist_ok=True)
        
    def copy_content(self, copy_to: "Target"):
        if not self.exists:
            return
        
        with open(self.file_path, "rb") as read_from:
            copy_to.create_path()
            with open(self.file_path, "wb") as write_to:
                write_to.write(read_from.read())

    def stream_into(self, r: requests.Response):
        self.create_path()
        
        chunk_size = 1024
        total_size = int(r.headers.get('content-length'))
        initial_pos = 0
        
        with open(self.file_path,'wb') as f:      
            for chunk in r.iter_content(chunk_size=chunk_size):
                size = f.write(chunk) 
        
        """
        # doesn't work yet due to
        # https://github.com/tqdm/tqdm/issues/261
        
        
        with open(self.file_path,'wb') as f, \
        tqdm(desc=self._file, total=total_size, unit='iB', unit_scale=True, unit_divisor=chunk_size) as pbar:      
            for chunk in r.iter_content(chunk_size=chunk_size):
                size = f.write(chunk) 
                pbar.update(size)
        """
