from typing import List

import mutagen
from mutagen.id3 import ID3, USLT

from ..utils.shared import *
from . import genius
from ..database import (
    Song,
    cache,
    Lyrics,
    Target
)

logger = LYRICS_LOGGER

"""
This whole Part is bodgy as hell and I need to rewrite this little file urgently. genius.py is really clean though :3
Just wanted to get it to work.
 - lyrics need to be put in the database and everything should continue from there then
"""

"""
https://cweiske.de/tagebuch/rhythmbox-lyrics.htm
Rythmbox, my music player doesn't support ID3 lyrics (USLT) yet, so I have to find something else
Lyrics in MP3 ID3 tags (SYLT/USLT) is still missing, because GStreamer does not support that yet.

One possible sollution would be to use ogg/vorbis files. Those lyrics are supported in rythmbox
'So, the next Rhythmbox release (3.5.0 or 3.4.2) will read lyrics directly from ogg/vorbis files, using the LYRICS and SYNCLYRICS tags.'
Another possible sollution (probaply the better one cuz I dont need to refactor whole metadata AGAIN)
would be to write a Rhythmbox plugin that fetches lyrics from ID3 USLT

I have written that Rhythmbox plugin: https://github.com/HeIIow2/rythmbox-id3-lyrics-support
"""


# https://www.programcreek.com/python/example/63462/mutagen.mp3.EasyMP3
# https://code.activestate.com/recipes/577138-embed-lyrics-into-mp3-files-using-mutagen-uslt-tag/


def add_lyrics(target: Target, lyrics):
    if not os.path.exists(target.file):
        return

    try:
        tags = ID3(target.file)
    except mutagen.id3.ID3NoHeaderError:
        return

    logger.info(f"adding lyrics to the file {target.file}")

    uslt_output = USLT(encoding=3, lang=lyrics.language, desc=u'desc', text=lyrics.text)
    tags["USLT::'eng'"] = uslt_output
    tags.save(target.file)


def fetch_single_lyrics(song: Song):
    logger.info(f"try fetching lyrics for {song}")

    lyrics_list: List[Lyrics] = genius.fetch_lyrics(song)
    """
    for artist in song.get_artist_names():
        lyrics.extend(genius.search(artist, song.title))
    """
    if len(lyrics_list) == 0:
        return

    logger.info(f"found lyrics for {song}")
    song.lyrics.extend(lyrics_list)
    print(lyrics_list)
    cache.add_lyrics(song=song, lyrics=lyrics_list[0])
    add_lyrics(song.target, lyrics_list[0])

    # cache.add_lyrics(song.id, lyrics=lyrics[0])
    # add_lyrics(song.target.file, lyrics[0])


def fetch_lyrics(songs: List[Song]):
    for song in songs:
        fetch_single_lyrics(song)
