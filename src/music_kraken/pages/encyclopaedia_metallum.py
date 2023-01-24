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
    Album
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
        endpoint = "https://www.metal-archives.com/search/ajax-advanced/searching/songs/?songTitle={song}&bandName={artist}&releaseTitle={album}&lyrics=&genre=&sEcho=1&iColumns=5&sColumns=&iDisplayStart=0&iDisplayLength=200&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&_=1674550595663"
        
        r = cls.API_SESSION.get(endpoint.format(song=query.song_str, artist=query.artist_str, album=query.album_str))
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {endpoint.format(song=query.song_str, artist=query.artist_str, album=query.album_str)}")
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
        endpoint = "https://www.metal-archives.com/search/ajax-advanced/searching/albums/?bandName={artist}&releaseTitle={album}&releaseYearFrom=&releaseMonthFrom=&releaseYearTo=&releaseMonthTo=&country=&location=&releaseLabelName=&releaseCatalogNumber=&releaseIdentifiers=&releaseRecordingInfo=&releaseDescription=&releaseNotes=&genre=&sEcho=1&iColumns=3&sColumns=&iDisplayStart=0&iDisplayLength=200&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&_=1674563943747"
        
        r = cls.API_SESSION.get(endpoint.format(artist=query.artist_str, album=query.album_str))
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {endpoint.format(song=query.song_str, artist=query.artist_str, album=query.album_str)}")
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
            cls.get_artist_from_json(html=raw_artist[0], genre=raw_artist[1], country=raw_artist[2]) 
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
            cls.get_artist_from_json(html=raw_artist[0], genre=raw_artist[1], country=raw_artist[2]) 
            for raw_artist in r.json()['aaData']
        ]

    @classmethod
    def get_artist_from_json(cls, html=None, genre=None, country=None) -> Artist:
        """
        TODO parse the country to a standart
        """
        # parse the html
        # parse the html for the band name and link on metal-archives
        soup = BeautifulSoup(html, 'html.parser')
        anchor = soup.find('a')
        artist_name = anchor.text
        artist_url = anchor.get('href')
        artist_id = int(artist_url.split("/")[-1])

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
            sources=[
                Source(SourcePages.ENCYCLOPAEDIA_METALLUM, artist_url)
            ],
            notes = notes
        )

    @classmethod
    def get_album_from_json(cls, album_html=None, release_type=None, artist_html=None) -> Album:
        # parse the html
        # <a href="https://www.metal-archives.com/albums/Ghost_Bath/Self_Loather/970834">Self Loather</a>'
        soup = BeautifulSoup(album_html, 'html.parser')
        anchor = soup.find('a')
        album_name = anchor.text
        album_url = anchor.get('href')
        album_id = int(album_url.split("/")[-1])

        """
        TODO implement release type
        TODO add artist argument to 
        """
        return Album(
            id_=album_id,
            title=album_name,
            sources=[
                Source(SourcePages.ENCYCLOPAEDIA_METALLUM, album_url)
            ]
        )

    @classmethod
    def get_song_from_json(cls, artist_html=None, album_html=None, release_type=None, title=None, lyrics_html=None) -> Song:
        song_id = None
        if lyrics_html is not None:
            # <a href="javascript:;" id="lyricsLink_5948443" title="Toggle lyrics display" class="viewLyrics iconContainer ui-state-default"><span class="ui-icon ui-icon-script">Edit song lyrics</span></a>
            soup = BeautifulSoup(lyrics_html, 'html.parser')
            anchor = soup.find('a')
            raw_song_id = anchor.get('id')
            song_id = raw_song_id.replace("lyricsLink_", "")
        
        return Song(
            id_=song_id,
            title=title,
            main_artist_list=[
                cls.get_artist_from_json(html=artist_html)
            ],
            album=cls.get_album_from_json(album_html=album_html, release_type=release_type, artist_html=artist_html)
        )

    @classmethod
    def fetch_artist_details(cls, artist: Artist) -> Artist:
        relevant_source = None
        for source in artist.sources:
            if source.page_enum == cls.SOURCE_TYPE:
                relevant_source = source
                break
        if relevant_source is None:
            return artist
        
        print(relevant_source.url)
        return artist