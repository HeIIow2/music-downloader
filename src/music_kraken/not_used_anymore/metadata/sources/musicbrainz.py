from typing import List
import musicbrainzngs

from src.music_kraken.database import (
    Artist,
    Album,
    Song
)
from src.music_kraken.utils.object_handeling import (
    get_elem_from_obj
)


def get_artist(flat: bool = False) -> Artist:
    # getting the flat artist
    artist_object = Artist()
    if flat:
        return artist_object
    # get additional stuff like discography
    return artist_object


def get_album(flat: bool = False) -> Album:
    # getting the flat album object
    album_object = Album()
    if flat:
        return album_object
    # get additional stuff like tracklist
    return album_object


def get_song(mb_id: str, flat: bool = False) -> Song:
    # getting the flat song object
    try:
        result = musicbrainzngs.get_recording_by_id(mb_id,
                                                    includes=["artists", "releases", "recording-rels", "isrcs",
                                                              "work-level-rels"])
    except musicbrainzngs.musicbrainz.NetworkError:
        return

    recording_data = result['recording']

    song_object = Song(
        mb_id=mb_id,
        title=recording_data['title'],
        length=get_elem_from_obj(recording_data, ['length']),
        isrc=get_elem_from_obj(recording_data, ['isrc-list', 0])
    )
    if flat:
        return song_object

    # fetch additional stuff
    artist_data_list = get_elem_from_obj(recording_data, ['artist-credit'], return_if_none=[])
    for artist_data in artist_data_list:
        mb_artist_id = get_elem_from_obj(artist_data, ['artist', 'id'])

    release_data = get_elem_from_obj(recording_data, ['release-list', -1])
    mb_release_id = get_elem_from_obj(release_data, ['id'])
    return song_object
