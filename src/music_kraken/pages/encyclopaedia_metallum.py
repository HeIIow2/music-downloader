from typing import List
import requests
from bs4 import BeautifulSoup

from ..utils.shared import (
    ENCYCLOPAEDIA_METALLUM_LOGGER as LOGGER
)

from .abstract import Page
from ..database import (
    MusicObject,
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    ID3Timestamp
)
from ..utils import (
    string_processing
)


class EncyclopaediaMetallum(Page):
    API_SESSION: requests.Session = requests.Session()
    API_SESSION.headers = {
        "Host": "www.metal-archives.com",
        "Connection": "keep-alive"
    }

    SOURCE_TYPE = SourcePages.ENCYCLOPAEDIA_METALLUM

    @classmethod
    def search_by_query(cls, query: str) -> List[MusicObject]:
        query_obj = cls.Query(query)

        if query_obj.is_raw:
            return cls.simple_search(query_obj)
        return cls.advanced_search(query_obj)

    @classmethod
    def advanced_search(cls, query: Page.Query) -> List[MusicObject]:
        if query.song is not None:
            return cls.search_for_song(query=query)
        if query.album is not None:
            return cls.search_for_album(query=query)
        if query.artist is not None:
            return cls.search_for_artist(query=query)
        return []

    @classmethod
    def search_for_song(cls, query: Page.Query) -> List[Song]:
        endpoint = "https://www.metal-archives.com/search/ajax-advanced/searching/songs/?songTitle={song}&bandName={" \
                   "artist}&releaseTitle={album}&lyrics=&genre=&sEcho=1&iColumns=5&sColumns=&iDisplayStart=0" \
                   "&iDisplayLength=200&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&_" \
                   "=1674550595663"

        r = cls.API_SESSION.get(endpoint.format(song=query.song_str, artist=query.artist_str, album=query.album_str))
        if r.status_code != 200:
            LOGGER.warning(
                f"code {r.status_code} at {endpoint.format(song=query.song_str, artist=query.artist_str, album=query.album_str)}")
            return []

        return [cls.get_song_from_json(
            artist_html=raw_song[0],
            album_html=raw_song[1],
            release_type=raw_song[2],
            title=raw_song[3],
            lyrics_html=raw_song[4]
        ) for raw_song in r.json()['aaData']]

    @classmethod
    def search_for_album(cls, query: Page.Query) -> List[Album]:
        endpoint = "https://www.metal-archives.com/search/ajax-advanced/searching/albums/?bandName={" \
                   "artist}&releaseTitle={album}&releaseYearFrom=&releaseMonthFrom=&releaseYearTo=&releaseMonthTo" \
                   "=&country=&location=&releaseLabelName=&releaseCatalogNumber=&releaseIdentifiers" \
                   "=&releaseRecordingInfo=&releaseDescription=&releaseNotes=&genre=&sEcho=1&iColumns=3&sColumns" \
                   "=&iDisplayStart=0&iDisplayLength=200&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&_=1674563943747"

        r = cls.API_SESSION.get(endpoint.format(artist=query.artist_str, album=query.album_str))
        if r.status_code != 200:
            LOGGER.warning(
                f"code {r.status_code} at {endpoint.format(song=query.song_str, artist=query.artist_str, album=query.album_str)}")
            return []

        return [cls.get_album_from_json(
            artist_html=raw_album[0],
            album_html=raw_album[1],
            release_type=[2]
        ) for raw_album in r.json()['aaData']]

    @classmethod
    def search_for_artist(cls, query: Page.Query) -> List[Artist]:
        endpoint = "https://www.metal-archives.com/search/ajax-advanced/searching/bands/?bandName={artist}&genre=&country=&yearCreationFrom=&yearCreationTo=&bandNotes=&status=&themes=&location=&bandLabelName=&sEcho=1&iColumns=3&sColumns=&iDisplayStart=0&iDisplayLength=200&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&_=1674565459976"

        r = cls.API_SESSION.get(endpoint.format(artist=query.artist))
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {endpoint.format(artist=query.artist)}")
            return []

        return [
            cls.get_artist_from_json(artist_html=raw_artist[0], genre=raw_artist[1], country=raw_artist[2])
            for raw_artist in r.json()['aaData']
        ]

    @classmethod
    def simple_search(cls, query: Page.Query) -> List[Artist]:
        """
        Searches the default endpoint from metal archives, which intern searches only
        for bands, but it is the default, thus I am rolling with it
        """
        endpoint = "https://www.metal-archives.com/search/ajax-band-search/?field=name&query={query}&sEcho=1&iColumns=3&sColumns=&iDisplayStart=0&iDisplayLength=200&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2"

        r = cls.API_SESSION.get(endpoint.format(query=query))
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {endpoint.format(query=query.query)}")
            return []

        return [
            cls.get_artist_from_json(artist_html=raw_artist[0], genre=raw_artist[1], country=raw_artist[2])
            for raw_artist in r.json()['aaData']
        ]

    @classmethod
    def get_artist_from_json(cls, artist_html=None, genre=None, country=None) -> Artist:
        """
        TODO parse the country to a standart
        """
        # parse the html
        # parse the html for the band name and link on metal-archives
        soup = BeautifulSoup(artist_html, 'html.parser')
        anchor = soup.find('a')
        artist_name = anchor.text
        artist_url = anchor.get('href')
        artist_id = artist_url.split("/")[-1]

        notes = f"{artist_name} is a {genre} band from {country}"

        anchor.decompose()
        strong = soup.find('strong')
        if strong is not None:
            strong.decompose()
            akronyms_ = soup.text[2:-2].split(', ')
            notes += f"aka {akronyms_}"
        notes += "."

        return Artist(
            id_=artist_id,
            name=artist_name,
            source_list=[
                Source(SourcePages.ENCYCLOPAEDIA_METALLUM, artist_url)
            ],
            notes=notes
        )

    @classmethod
    def get_album_from_json(cls, album_html=None, release_type=None, artist_html=None) -> Album:
        # parse the html
        # <a href="https://www.metal-archives.com/albums/Ghost_Bath/Self_Loather/970834">Self Loather</a>'
        soup = BeautifulSoup(album_html, 'html.parser')
        anchor = soup.find('a')
        album_name = anchor.text
        album_url = anchor.get('href')
        album_id = album_url.split("/")[-1]

        """
        TODO implement release type
        """
        return Album(
            id_=album_id,
            title=album_name,
            source_list=[
                Source(SourcePages.ENCYCLOPAEDIA_METALLUM, album_url)
            ],
            artists=[
                cls.get_artist_from_json(artist_html=artist_html)
            ]
        )

    @classmethod
    def get_song_from_json(cls, artist_html=None, album_html=None, release_type=None, title=None,
                           lyrics_html=None) -> Song:
        song_id = None
        if lyrics_html is not None:
            soup = BeautifulSoup(lyrics_html, 'html.parser')
            anchor = soup.find('a')
            raw_song_id = anchor.get('id')
            song_id = raw_song_id.replace("lyricsLink_", "")

        return Song(
            id_=song_id,
            title=title,
            main_artist_list=[
                cls.get_artist_from_json(artist_html=artist_html)
            ],
            album=cls.get_album_from_json(album_html=album_html, release_type=release_type, artist_html=artist_html),
            source_list=[
                Source(SourcePages.ENCYCLOPAEDIA_METALLUM, song_id)
            ]
        )

    @classmethod
    def fetch_artist_discography(cls, artist: Artist, ma_artist_id: str) -> Artist:
        """
        TODO
        I'd guess this funktion has quite some possibility for optimizations
        in form of performance and clean code
        """
        discography_url = "https://www.metal-archives.com/band/discography/id/{}/tab/all"
        
        # prepare tracklist
        album_by_url = dict()
        album_by_name = dict()
        for album in artist.main_albums:
            album_by_name[string_processing.unify(album.title)] = album
            for source in album.get_sources_from_page(cls.SOURCE_TYPE):
                album_by_url[source.url] = album
        old_discography = artist.main_albums.copy()
        # save the ids of the albums, that are added to this set, so I can
        # efficiently add all leftover albums from the discography to the new one
        used_ids = set()

        new_discography: List[Album] = []

        # make the request
        r = cls.API_SESSION.get(discography_url.format(ma_artist_id))
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {discography_url.format(ma_artist_id)}")
            return artist

        # parse the html
        soup = BeautifulSoup(r.text, 'html.parser')

        tbody_soup = soup.find('tbody')
        for tr_soup in tbody_soup.find_all('tr'):
            td_list = tr_soup.findChildren(recursive=False)

            album_soup = td_list[0]
            album_name = album_soup.text
            album_url = album_soup.find('a').get('href')
            album_id = album_url.split('/')[-1]
            album_type = td_list[1].text
            album_year = td_list[2].text
            
            unified_name = string_processing.unify(album_name)

            album_obj: Album = Album(id_=album_id)

            if album_url in album_by_url:
                album_obj = album_by_url[album_url]
                used_ids.add(album_obj.id)

            elif unified_name in album_by_name:
                album_obj = album_by_name[unified_name]
                album_obj.add_source(Source(SourcePages.ENCYCLOPAEDIA_METALLUM, album_url))
                used_ids.add(album_obj.id)
            else:
                album_obj.add_source(Source(SourcePages.ENCYCLOPAEDIA_METALLUM, album_url))

            album_obj.title = album_name
            album_obj.album_type = album_type
            try:
                album_obj.date = ID3Timestamp(year=int(album_year))
            except ValueError():
                pass
            
            new_discography.append(album_obj)

        # add the albums back, which weren't on this page
        for old_object in old_discography:
            if old_object.id not in used_ids:
                new_discography.append(old_object)

        artist.main_albums = new_discography

        return artist

    @classmethod
    def fetch_artist_sources(cls, artist: Artist, ma_artist_id: str) -> Artist:
        sources_url = "https://www.metal-archives.com/link/ajax-list/type/band/id/{}"

        # make the request
        r = cls.API_SESSION.get(sources_url.format(ma_artist_id))
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {sources_url.format(ma_artist_id)}")
            return artist

        print(r.text)

        return artist

    @classmethod
    def fetch_artist_details(cls, artist: Artist) -> Artist:
        source_list = artist.get_sources_from_page(cls.SOURCE_TYPE)
        if len(source_list) == 0:
            return artist

        # taking the fist source, cuz I only need one and multiple sources don't make that much sense
        source = source_list[0]
        artist_id = source.url.split("/")[-1]
        print(source)
        print("id", artist_id)

        """
        https://www.metal-archives.com/bands/Ghost_Bath/3540372489
        https://www.metal-archives.com/band/discography/id/3540372489/tab/all
        ---review---
        https://www.metal-archives.com/review/ajax-list-band/id/3540372489/json/1?sEcho=1&iColumns=4&sColumns=&iDisplayStart=0&iDisplayLength=200&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&iSortCol_0=3&sSortDir_0=desc&iSortingCols=1&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&_=1675155257133
        ---simmilar-bands---
        https://www.metal-archives.com/band/ajax-recommendations/id/3540372489
        ---external-sources---
        https://www.metal-archives.com/link/ajax-list/type/band/id/3540372489
        """

        # SIMPLE METADATA

        # DISCOGRAPHY
        artist = cls.fetch_artist_discography(artist, artist_id)

        # External Sources
        artist = cls.fetch_artist_sources(artist, artist_id)

        return artist
