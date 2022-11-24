from typing import List

from ..database.song import Song as song_object
from . import (
    fetch_source,
    fetch_audio
)

def fetch_sources(songs: List[song_object], skip_existing_files: bool = False):
    fetch_source.Download.fetch_sources(songs=songs, skip_existing_files=skip_existing_files)

def fetch_audios(songs: List[song_object], override_existing: bool = False):
    fetch_audio.Download.fetch_audios(songs=songs, override_existing=override_existing)

