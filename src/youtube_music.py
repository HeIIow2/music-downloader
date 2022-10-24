import youtube_dl
import pandas as pd
import logging
import time

import phonetic_compares

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
YOUTUBE_URL_KEY = 'webpage_url'
WAIT_BETWEEN_BLOCK = 10
MAX_TRIES = 3


def get_youtube_from_isrc(isrc: str):
    # https://stackoverflow.com/questions/63388364/searching-youtube-videos-using-youtube-dl
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        video = ydl.extract_info(f"ytsearch:{isrc}", download=False)['entries'][0]
    print(type(video))
    if YOUTUBE_URL_KEY not in video:
        return None
    return {
        'url': video[YOUTUBE_URL_KEY],
        'title': video['title']
    }


def get_youtube_url(row):
    if pd.isna(row['isrc']):
        return None
    real_title = row['title'].lower()

    result = get_youtube_from_isrc(row['isrc'])
    video_title = result['title'].lower()

    match, distance = phonetic_compares.match_titles(video_title, real_title)

    if match:
        logging.warning(
            f"dont downloading {result['url']} cuz the phonetic distance ({distance}) between {real_title} and {video_title} is to high.")
        return None
    return result['url']


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
