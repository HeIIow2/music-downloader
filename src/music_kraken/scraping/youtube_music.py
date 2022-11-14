from typing import List

import youtube_dl
import logging
import time

from ..utils import phonetic_compares

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
YOUTUBE_URL_KEY = 'webpage_url'
YOUTUBE_TITLE_KEY = 'title'
WAIT_BETWEEN_BLOCK = 10
MAX_TRIES = 3


def get_youtube_from_isrc(isrc: str) -> List[dict]:
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


def get_youtube_url(row):
    if row['isrc'] is None:
        return None

    real_title = row['title'].lower()

    final_result = None
    results = get_youtube_from_isrc(row['isrc'])
    for result in results:
        video_title = result['title'].lower()
        match, distance = phonetic_compares.match_titles(video_title, real_title)

        if match:
            logging.warning(
                f"dont downloading {result['url']} cuz the phonetic distance ({distance}) between {real_title} and {video_title} is to high.")
            continue

        final_result = result

    if final_result is None:
        return None
    return final_result['url']


def download(row, trie: int = 0):
    url = row['url']
    file_ = row['file']
    options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'keepvideo': False,
        'outtmpl': file_
    }

    try:
        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([url])
    except youtube_dl.utils.DownloadError:
        logging.warning(f"youtube blocked downloading. ({trie}-{MAX_TRIES})")
        if trie >= MAX_TRIES:
            logging.warning("too many tries, returning")
        logging.warning(f"retrying in {WAIT_BETWEEN_BLOCK} seconds again")
        time.sleep(WAIT_BETWEEN_BLOCK)
        return download(row, trie=trie+1)


if __name__ == "__main__":
    # example isrc that exists on YouTube music
    ISRC = "DEUM71500715"
    result = get_youtube_from_isrc(ISRC)
    print(result)
    result = get_youtube_from_isrc("aslhfklasdhfjklasdfjkhasdjlfhlasdjfkuuiueiw")
    print(result)
