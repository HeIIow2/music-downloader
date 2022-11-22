from typing import List

import youtube_dl
import time

from ...utils.shared import *
from ...utils import phonetic_compares
from .source import AudioSource

from ...database import song as song_objects


logger = YOUTUBE_LOGGER

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
YOUTUBE_URL_KEY = 'webpage_url'
YOUTUBE_TITLE_KEY = 'title'
WAIT_BETWEEN_BLOCK = 10
MAX_TRIES = 3


class Youtube(AudioSource):
    @classmethod
    def get_youtube_from_isrc(cls, isrc: str) -> List[dict]:
        # https://stackoverflow.com/questions/63388364/searching-youtube-videos-using-youtube-dl
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                videos = ydl.extract_info(f"ytsearch:{isrc}", download=False)['entries']
            except youtube_dl.utils.DownloadError:
                return []

        return [{
            'url': video[YOUTUBE_URL_KEY],
            'title': video[YOUTUBE_TITLE_KEY]
        } for video in videos]

    @classmethod
    def fetch_source(cls, song: song_objects.Song):
        # https://stackoverflow.com/questions/63388364/searching-youtube-videos-using-youtube-dl
        super().fetch_source(song)

        if not song.has_isrc():
            return None

        real_title = song.title.lower()

        final_result = None
        results = cls.get_youtube_from_isrc(song.isrc)
        for result in results:
            video_title = result['title'].lower()
            match, distance = phonetic_compares.match_titles(video_title, real_title)

            if match:
                # logger.warning(
                #     f"dont downloading {result['url']} cuz the phonetic distance ({distance}) between {real_title} and {video_title} is to high.")
                continue

            final_result = result

        if final_result is None:
            return None
        logger.info(f"found video {final_result}")
        return final_result['url']

    @classmethod
    def fetch_audio(cls, song: song_objects.Song, src: song_objects.Source, trie: int=0):
        super().fetch_audio(song, src)
        if song.target.file is None or song.target.path is None:
            logger.warning(f"target hasn't been set. Can't download. Most likely a bug.")
            return False

        options = {
            'format': 'bestaudio/best',
            'keepvideo': False,
            'outtmpl': song.target.file
        }

        # downloading
        try:
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([src.url])

        except youtube_dl.utils.DownloadError:
            # retry when failing
            logger.warning(f"youtube blocked downloading. ({trie}-{MAX_TRIES})")
            if trie >= MAX_TRIES:
                logger.warning("too many tries, returning")
                return False
            logger.warning(f"retrying in {WAIT_BETWEEN_BLOCK} seconds again")
            time.sleep(WAIT_BETWEEN_BLOCK)
            return cls.fetch_audio(song, src, trie=trie + 1)

