from typing import List

import musicbrainzngs
import pandas as pd
import logging
from datetime import date

import sqlite3

from object_handeling import get_elem_from_obj, parse_music_brainz_date

# I don't know if it would be feesable to set up my own mb instance
# https://github.com/metabrainz/musicbrainz-docker

mb_log = logging.getLogger("musicbrainzngs")
mb_log.setLevel(logging.WARNING)
musicbrainzngs.set_useragent("metadata receiver", "0.1", "https://github.com/HeIIow2/music-downloader")


# IMPORTANT
# https://python-musicbrainzngs.readthedocs.io/en/v0.7.1/api/#getting-data

class Artist:
    def __init__(
            self,
            musicbrainz_artistid: str,
            release_groups: List = [],
            new_release_groups: bool = True
    ):
        """
        release_groups: list
        """
        self.release_groups = release_groups

        self.musicbrainz_artistid = musicbrainz_artistid

        result = musicbrainzngs.get_artist_by_id(self.musicbrainz_artistid, includes=["release-groups", "releases"])
        artist_data = get_elem_from_obj(result, ['artist'], return_if_none={})

        self.artist = get_elem_from_obj(artist_data, ['name'])

        logging.info(f"artist: {self}")
        if not new_release_groups:
            return
        # sort all release groups by date and add album sort to have them in chronological order.
        release_groups = artist_data['release-group-list']
        for i, release_group in enumerate(release_groups):
            release_groups[i]['first-release-date'] = parse_music_brainz_date(release_group['first-release-date'])
        release_groups.sort(key=lambda x: x['first-release-date'])

        for i, release_group in enumerate(release_groups):
            self.release_groups.append(ReleaseGroup(
                musicbrainz_releasegroupid=release_group['id'],
                artists=[self],
                albumsort=i + 1
            ))

    def __str__(self):
        newline = "\n"
        return f"id: {self.musicbrainz_artistid}\nname: {self.artist}\n{newline.join([str(release_group) for release_group in self.release_groups])}"


class ReleaseGroup:
    def __init__(
            self,
            musicbrainz_releasegroupid: str,
            artists: List[Artist] = [],
            albumsort: int = None,
            only_download_distinct_releases: bool = True
    ):
        """
        split_artists: list -> if len > 1: album_artist=VariousArtists
        releases: list
        """

        self.musicbrainz_releasegroupid = musicbrainz_releasegroupid
        self.artists = artists
        self.releases = []

        result = musicbrainzngs.get_release_group_by_id(musicbrainz_releasegroupid,
                                                        includes=["artist-credits", "releases"])
        release_group_data = get_elem_from_obj(result, ['release-group'], return_if_none={})
        artist_datas = get_elem_from_obj(release_group_data, ['artist-credit'], return_if_none={})
        release_datas = get_elem_from_obj(release_group_data, ['release-list'], return_if_none={})

        for artist_data in artist_datas:
            artist_id = get_elem_from_obj(artist_data, ['artist', 'id'])
            if artist_id is None:
                continue
            self.append_artist(artist_id)
        self.albumartist = "Various Artists" if len(self.artists) >= 1 else self.artists[0].artist

        self.albumsort = albumsort
        self.musicbrainz_albumtype = get_elem_from_obj(release_group_data, ['primary-type'])
        self.compilation = "1" if self.musicbrainz_albumtype == "Compilation" else None

        if only_download_distinct_releases:
            self.append_distinct_releases(release_datas)
        else:
            self.append_all_releases(release_datas)

    def __str__(self):
        newline = "\n"
        return f"{newline.join([str(release_group) for release_group in self.releases])}"

    def append_artist(self, artist_id: str) -> Artist:
        for existing_artist in self.artists:
            if artist_id == existing_artist.musicbrainz_artistid:
                return existing_artist
        new_artist = Artist(artist_id, release_groups=[self], new_release_groups=False)
        self.artists.append(new_artist)
        return new_artist

    def append_release(self, release_data: dict):
        musicbrainz_albumid = get_elem_from_obj(release_data, ['id'])
        if musicbrainz_albumid is None:
            return
        self.releases.append(Release(musicbrainz_albumid, release_group=self))

    def append_distinct_releases(self, release_datas: List[dict]):
        titles = {}

        for release_data in release_datas:
            title = get_elem_from_obj(release_data, ['title'])
            if title is None:
                continue
            titles[title] = release_data

        for key in titles:
            self.append_release(titles[key])

    def append_all_releases(self, release_datas: List[dict]):
        for release_data in release_datas:
            self.append_release(release_data)


class Release:
    def __init__(
            self,
            musicbrainz_albumid: str,
            release_group: ReleaseGroup = None
    ):
        """
        release_group: ReleaseGroup
        tracks: list
        """
        self.musicbrainz_albumid = musicbrainz_albumid
        self.release_group = release_group
        self.tracklist = []

        result = musicbrainzngs.get_release_by_id(self.musicbrainz_albumid, includes=["recordings", "labels"])
        release_data = get_elem_from_obj(result, ['release'], return_if_none={})
        label_data = get_elem_from_obj(release_data, ['label-info-list'], return_if_none={})
        recording_datas = get_elem_from_obj(release_data, ['medium-list', 0, 'track-list'], return_if_none=[])

        self.title = get_elem_from_obj(release_data, ['title'])
        self.copyright = get_elem_from_obj(label_data, [0, 'label', 'name'])

        logging.info(f"release {self}")
        self.append_recordings(recording_datas)

    def append_recordings(self, recording_datas: dict):
        for recording_data in recording_datas:
            musicbrainz_releasetrackid = get_elem_from_obj(recording_data, ['id'])
            if musicbrainz_releasetrackid is None:
                continue

            self.tracklist.append(musicbrainz_releasetrackid)

    def __str__(self):
        return f"{self.title} ©{self.copyright}"


class Track:
    def __init__(
            self,
            musicbrainz_releasetrackid: str,
            release: Release = None
    ):
        """
        release: Release
        feature_artists: list
        """

        self.musicbrainz_releasetrackid = musicbrainz_releasetrackid
        self.release = release


def download(option: dict):
    type_ = option['type']
    mb_id = option['id']

    metadata_list = []
    if type_ == "artist":
        artist = Artist(mb_id)
        print(artist)
    elif type_ == "release":
        metadata_list = download_release(mb_id)
    elif type_ == "track":
        metadata_list = download_track(mb_id)

    print(metadata_list)
    metadata_df = pd.DataFrame(metadata_list)
    # metadata_df.to_csv(os.path.join(self.temp, file))
    return metadata_df


def download_artist(mb_id):
    """
    Available includes: recordings, releases, release-groups, works, various-artists, discids, media, isrcs,
    aliases, annotation, area-rels, artist-rels, label-rels, place-rels, event-rels, recording-rels,
    release-rels, release-group-rels, series-rels, url-rels, work-rels, instrument-rels, tags, user-tags,
    ratings, user-ratings
    """

    metadata_list = []
    # from this dict everything will be taken
    following_data = {}

    result = musicbrainzngs.get_artist_by_id(mb_id, includes=["release-groups", "releases"])
    artist_data = result['artist']

    # sort all release groups by date and add album sort to have them in chronological order.
    release_groups = artist_data['release-group-list']
    for i, release_group in enumerate(release_groups):
        release_groups[i]['first-release-date'] = parse_music_brainz_date(release_group['first-release-date'])
    release_groups.sort(key=lambda x: x['first-release-date'])

    for i, release_group in enumerate(release_groups):
        release_groups[i]['albumsort'] = i + 1

    def numeric_release_type(release_type: str) -> int:
        if release_type == "Album" or release_type == "EP":
            return 1
        return 2

    release_groups.sort(key=lambda x: numeric_release_type(x['type']))

    for release_group in release_groups:
        download_release_groups()


def download_release(mb_id, album_sort: int = None):
    """
    Available includes: artists, labels, recordings, release-groups, media, artist-credits, discids, isrcs,
    recording-level-rels, work-level-rels, annotation, aliases, tags, user-tags, area-rels, artist-rels,
    label-rels, place-rels, event-rels, recording-rels, release-rels, release-group-rels, series-rels, url-rels,
    work-rels, instrument-rels
    """

    def get_additional_artist_info(mb_id_):
        r = musicbrainzngs.get_artist_by_id(mb_id_, includes=["releases"])

        album_sort = 0
        for i, release in enumerate(r["artist"]["release-list"]):
            id_ = release["id"]
            if id_ == mb_id:
                album_sort = i
                break

        return album_sort

    result = musicbrainzngs.get_release_by_id(mb_id, includes=["artists", "recordings", 'release-groups'])

    if album_sort is None:
        album_sort = get_additional_artist_info(
            get_elem_from_obj(result, ['release', 'artist-credit', 0, 'artist', 'id']))
    release_type = get_elem_from_obj(result, ['release', 'release-group', 'type'])

    tracklist_metadata = []

    is_various_artist = len(result['release']['artist-credit']) > 1
    tracklist = result['release']['medium-list'][0]['track-list']
    track_count = len(tracklist)
    for track in tracklist:
        track_id = track["recording"]["id"]
        this_track = track["position"]

        tracklist_metadata.extend(
            download_track(track_id, is_various_artist=is_various_artist, track=this_track,
                           total_tracks=track_count, album_sort=album_sort, album_type=release_type,
                           release_data=result['release']))

    return tracklist_metadata


def download_track(mb_id, is_various_artist: bool = None, track: int = None, total_tracks: int = None,
                   album_sort: int = None, album_type: str = None, release_data: dict = None):
    """
    TODO
    bpm     its kind of possible via the AcousticBrainz API. however, the data may not be of very good
            quality and AB is scheduled to go away in some time.

    compilation     Field that is used by iTunes to mark albums as compilation.
                    Either enter the value 1 or delete the field. https://en.wikipedia.org/wiki/Compilation_album
                    How should I get it? I don't fucking know. Now I do. Release Group Type is Compilation

    composer, copyright, discsubtitle
    'musicbrainz_discid',
    'asin',
    'performer',
    'catalognumber',
    'musicbrainz_releasetrackid',
    'musicbrainz_releasegroupid',
    'musicbrainz_workid',
    'acoustid_fingerprint',
    'acoustid_id'

    DONE

    album
    title
    artist
    albumartist
    tracknumber
    !!!albumsort can sort albums cronological
    titlesort is just set to the tracknumber to sort by track order to sort correctly
    isrc
    musicbrainz_artistid
    musicbrainz_albumid
    musicbrainz_albumartistid
    musicbrainz_albumstatus
    language
    musicbrainz_albumtype
    'releasecountry'
    'barcode'

    Album Art
    """
    """
    Available includes: artists, releases, discids, media, artist-credits, isrcs, work-level-rels, annotation, 
    aliases, tags, user-tags, ratings, user-ratings, area-rels, artist-rels, label-rels, place-rels, event-rels, 
    recording-rels, release-rels, release-group-rels, series-rels, url-rels, work-rels, instrument-rels 
    """

    result = musicbrainzngs.get_recording_by_id(mb_id, includes=["artists", "releases", "recording-rels", "isrcs",
                                                                 "work-level-rels"])
    recording_data = result['recording']
    isrc = get_elem_from_obj(recording_data, ['isrc-list', 0])

    if release_data is None:
        # choosing the last release, because it is the least likely one to be a single
        release_data = recording_data['release-list'][-1]
    mb_release_id = release_data['id']

    title = recording_data['title']

    artist = []
    mb_artist_ids = []
    for artist_ in recording_data['artist-credit']:
        name_ = get_elem_from_obj(artist_, ['artist', 'name'])
        if name_ is None:
            continue
        artist.append(name_)
        mb_artist_ids.append(get_elem_from_obj(artist_, ['artist', 'id']))

    def get_additional_artist_info(mb_id_):
        r = musicbrainzngs.get_artist_by_id(mb_id_, includes=["releases"])

        album_sort = 0
        for i, release in enumerate(r["artist"]["release-list"]):
            id_ = release["id"]
            if id_ == mb_release_id:
                album_sort = i
                break

        return album_sort

    def get_additional_release_info(mb_id_):
        r = musicbrainzngs.get_release_by_id(mb_id_,
                                             includes=["artists", "recordings", "recording-rels", 'release-groups'])
        is_various_artist_ = len(r['release']['artist-credit']) > 1
        tracklist = r['release']['medium-list'][0]['track-list']
        track_count_ = len(tracklist)
        this_track_ = 0
        for track in tracklist:
            if track["recording"]["id"] == mb_id:
                this_track_ = track["position"]

        release_type = get_elem_from_obj(r, ['release', 'release-group', 'type'])

        return is_various_artist_, this_track_, track_count_, release_type

    album_id = get_elem_from_obj(release_data, ['id'])
    album = get_elem_from_obj(release_data, ['title'])
    album_status = get_elem_from_obj(release_data, ['status'])
    language = get_elem_from_obj(release_data, ['text-representation', 'language'])

    year = get_elem_from_obj(release_data, ['date'], lambda x: x.split("-")[0])
    date = get_elem_from_obj(release_data, ['date'])
    if is_various_artist is None or track is None or total_tracks is None or album_type is None:
        is_various_artist, track, total_tracks, album_type = get_additional_release_info(album_id)
    if album_sort is None:
        album_sort = get_additional_artist_info(mb_artist_ids[0])
    album_artist = "Various Artists" if is_various_artist else artist[0]
    album_artist_id = None if album_artist == "Various Artists" else mb_artist_ids[0]
    compilation = "1" if album_type == "Compilation" else None
    country = get_elem_from_obj(release_data, ['country'])
    barcode = get_elem_from_obj(release_data, ['barcode'])

    return [{
        'id': mb_id,
        'album': album,
        'title': title,
        'artist': artist,
        'album_artist': album_artist,
        'tracknumber': str(track),
        'albumsort': album_sort,
        'titlesort': track,
        'isrc': isrc,
        'date': date,
        'year': year,
        'musicbrainz_artistid': mb_artist_ids[0],
        'musicbrainz_albumid': mb_release_id,
        'musicbrainz_albumartistid': album_artist_id,
        'musicbrainz_albumstatus': album_status,
        'total_tracks': total_tracks,
        'language': language,
        'musicbrainz_albumtype': album_type,
        'compilation': compilation,
        'releasecountry': country,
        'barcode': barcode
    }]


if __name__ == "__main__":
    """
    import tempfile
    import os

    TEMP_FOLDER = "music-downloader"
    TEMP_DIR = os.path.join(tempfile.gettempdir(), TEMP_FOLDER)
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)
    """
    logging.basicConfig(level=logging.DEBUG)
    sqliteConnection = sqlite3.connect('sql.db')

    download({'id': '5cfecbe4-f600-45e5-9038-ce820eedf3d1', 'type': 'artist'})
    # download({'id': '4b9af532-ef7e-42ab-8b26-c466327cb5e0', 'type': 'release'})
    # download({'id': 'c24ed9e7-6df9-44de-8570-975f1a5a75d1', 'type': 'track'})
