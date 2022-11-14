import mutagen
from mutagen.id3 import ID3, USLT


from ..metadata import database as db
from ..utils.shared import *
from . import genius

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


def add_lyrics(file_name, lyrics):
    file_path = os.path.join(MUSIC_DIR, file_name)
    if not os.path.exists(file_path):
        return

    try:
        tags = ID3(file_path)
    except mutagen.id3.ID3NoHeaderError:
        return

    logger.info(f"adding lyrics to the file {file_path}")

    uslt_output = USLT(encoding=3, lang=lyrics.lang, desc=u'desc', text=lyrics.lyrics)
    tags["USLT::'eng'"] = uslt_output
    tags.save(file_path)


def fetch_single_lyrics(row: dict):
    artists = [artist['name'] for artist in row['artists']]
    track = row['title']
    id_ = row['id']

    logger.info(f"try fetching lyrics for \"{track}\" by \"{', '.join(artists)}")

    lyrics = []
    for artist in artists:
        lyrics.extend(genius.search(artist, track))
    if len(lyrics) == 0:
        return

    logger.info("found lyrics")
    database.add_lyrics(id_, lyrics=lyrics[0])
    add_lyrics(row['file'], lyrics[0])


def fetch_lyrics():
    for row in database.get_tracks_for_lyrics():
        fetch_single_lyrics(row)


if __name__ == "__main__":
    import tempfile
    import os

    temp_folder = "music-downloader"
    temp_dir = os.path.join(tempfile.gettempdir(), temp_folder)
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    logging.basicConfig(level=logging.DEBUG)
    db_logger = logging.getLogger("database")
    db_logger.setLevel(logging.DEBUG)

    database = db.Database(os.path.join(temp_dir, "metadata.db"),
                           os.path.join(temp_dir, "database_structure.sql"),
                           "https://raw.githubusercontent.com/HeIIow2/music-downloader/new_metadata/assets/database_structure.sql",
                           db_logger,
                           reset_anyways=False)

    fetch_lyrics()
