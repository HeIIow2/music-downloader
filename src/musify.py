import logging
import requests

session = requests.Session()
session.headers = {
    "Connection": "keep-alive",
    "Referer": "https://musify.club/"
}

def get_musify_url(row):
    title = row['title']
    artists = row['artist']

    url = f"https://musify.club/search/suggestions?term={title}"

    r = session.get(url=url)
    if r.status_code == 200:
        autocomplete = r.json()
        for row in autocomplete:
            if any(a in row['label'] for a in artists) and "/track" in row['url']:
                return get_download_link(row['url'])

    return None

def get_download_link(default_url):
    # https://musify.club/track/dl/18567672/rauw-alejandro-te-felicito-feat-shakira.mp3
    # /track/sundenklang-wenn-mein-herz-schreit-3883217'

    file_ = default_url.split("/")[-1]
    musify_id = file_.split("-")[-1]
    musify_name = "-".join(file_.split("-")[:-1])

    logging.info(f"https://musify.club/track/dl/{musify_id}/{musify_name}.mp3")

    return f"https://musify.club/track/dl/{musify_id}/{musify_name}.mp3"

def download_from_musify(file, url):
    logging.info(f"downloading: '{url}'")
    r = session.get(url)
    if r.status_code != 200:
        if r.status_code == 404:
            logging.warning(f"{url} was not found")
            return -1
        raise ConnectionError(f"\"{url}\" returned {r.status_code}: {r.text}")
    with open(file, "wb") as mp3_file:
        mp3_file.write(r.content)
    logging.info("finished")

def download(row):
    url = row['url']
    file_ = row['file']
    return download_from_musify(file_, url)
