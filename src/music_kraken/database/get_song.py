from typing import List

from .song import (
    Song,
    Source,
    Target,
    Metadata,
    Artist,
    LyricsContainer,
    Lyrics
)


def get_song_from_response(response: dict) -> Song:
    # artists
    artists = [Artist(id_=a['id'], name=a['name']) for a in response['artists']]

    # metadata
    metadata = Metadata()
    for key, value in response.items():
        metadata[key] = value
    metadata['artists'] = [a.name for a in artists]
    
    # sources
    sources: List[Source] = []
    for src in response['source']:
        if src['src'] is None:
            continue
        sources.append(Source(src))

    # target
    target = Target()
    target.set_file(response['file'])
    target.set_path(response['path'])

    # Lyrics
    lyrics_container = LyricsContainer()
    lyrics_container.append(Lyrics(text=response['lyrics'], language='en'))

    length = response['length']
    if length is not None:
        length = int(length)

    song = Song(
        id_=response['id'],
        mb_id=response['id'],
        title=response['title'],
        release=response['album'],
        isrc=response['isrc'],
        length=length,
        artists=artists,
        metadata=metadata,
        sources=sources,
        target=target
    )

    return song
