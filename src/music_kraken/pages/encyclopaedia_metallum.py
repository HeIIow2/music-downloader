from typing import List
import requests
from bs4 import BeautifulSoup
import pycountry

from ..utils.shared import (
    ENCYCLOPAEDIA_METALLUM_LOGGER as LOGGER
)

from .abstract import Page
from ..objects import (
    MusicObject,
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    ID3Timestamp,
    FormattedText,
    Label,
    Options
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
    def search_by_query(cls, query: str) -> Options:
        query_obj = cls.Query(query)

        if query_obj.is_raw:
            return cls.simple_search(query_obj)
        return cls.advanced_search(query_obj)

    @classmethod
    def advanced_search(cls, query: Page.Query) -> Options:
        if query.song is not None:
            return Options(cls.search_for_song(query=query))
        if query.album is not None:
            return Options(cls.search_for_album(query=query))
        if query.artist is not None:
            return Options(cls.search_for_artist(query=query))
        return Options

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
            notes=FormattedText(plaintext=notes)
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
    def fetch_artist_discography(cls, artist: Artist, ma_artist_id: str, flat: bool = False) -> Artist:
        """
        TODO
        I'd guess this funktion has quite some possibility for optimizations
        in form of performance and clean code
        """
        discography_url = "https://www.metal-archives.com/band/discography/id/{}/tab/all"

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
            date_obj = None
            try:
                date_obj = ID3Timestamp(year=int(album_year))
            except ValueError():
                pass

            artist.main_album_collection.append(
                Album(
                    id_=album_id,
                    title=album_name,
                    album_type=album_type,
                    date=date_obj,
                    source_list=[Source(SourcePages.ENCYCLOPAEDIA_METALLUM, album_url)]
                )
            )

        if not flat:
            for album in artist.main_album_collection:
                cls.fetch_album_details(album, flat=flat)

        return artist

    @classmethod
    def fetch_artist_sources(cls, artist: Artist, ma_artist_id: str) -> Artist:
        sources_url = "https://www.metal-archives.com/link/ajax-list/type/band/id/{}"

        # make the request
        r = cls.API_SESSION.get(sources_url.format(ma_artist_id))
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {sources_url.format(ma_artist_id)}")
            return artist

        soup = BeautifulSoup(r.text, 'html.parser')

        if soup.find("span",{"id": "noLinks"}) is not None:
            return artist

        artist_source = soup.find("div", {"id": "band_links_Official"})
        """
        TODO
        add a Label object to add the label sources from
        TODO
        maybe do merchandice stuff
        """
        merchandice_source = soup.find("div", {"id": "band_links_Official_merchandise"})
        label_source = soup.find("div", {"id": "band_links_Labels"})

        if artist_source is not None:
            for tr in artist_source.find_all("td"):
                a = tr.find("a")
                url = a.get("href")

                source = Source.match_url(url)
                if source is None:
                    continue

                artist.add_source(source)

        return artist

    @classmethod
    def fetch_artist_attributes(cls, artist: Artist, url: str) -> Artist:
        r = cls.API_SESSION.get(url)
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {url}")
            return artist

        soup = BeautifulSoup(r.text, 'html.parser')

        country: pycountry.Countrie = None
        formed_in_year: int = None
        genre: str = None
        lyrical_themes: List[str] = []
        label_name: str = None
        label_url: str = None

        band_stat_soup = soup.find("div", {"id": "band_stats"})
        for dl_soup in band_stat_soup.find_all("dl"):
            for title, data in zip(dl_soup.find_all("dt"), dl_soup.find_all("dd")):
                title_text = title.text

                if "Country of origin:" == title_text:
                    href = data.find('a').get('href')
                    country = pycountry.countries.get(alpha_2=href.split("/")[-1])
                    artist.country = country
                    continue

                # not needed: Location: Minot, North Dakota

                """
                TODO
                status: active
                need to do enums for that and add it to object
                """

                if "Formed in:" == title_text:
                    if not data.text.isnumeric():
                        continue
                    formed_in_year = int(data.text)
                    artist.formed_in = ID3Timestamp(year=formed_in_year)
                    continue
                if "Genre:" == title_text:
                    genre = data.text
                    artist.general_genre = genre
                    continue
                if "Lyrical themes:" == title_text:
                    lyrical_themes = data.text.split(", ")
                    artist.lyrical_themes = lyrical_themes
                    continue
                if "Current label:" == title_text:
                    label_name = data.text
                    label_anchor = data.find("a")
                    label_url = None
                    if label_anchor is not None:
                        label_url = label_anchor.get("href")
                        label_id = None
                        if type(label_url) is str and "/" in label_url:
                            label_id = label_url.split("/")[-1]
                        
                        artist.label_collection.append(
                            Label(
                                _id=label_id,
                                name=label_name,
                                source_list=[
                                    Source(cls.SOURCE_TYPE, label_url)
                                ]
                            ))


                """
                years active: 2012-present
                process this and add field to class
                """

        return artist

    @classmethod
    def fetch_band_notes(cls, artist: Artist, ma_artist_id: str) -> Artist:
        endpoint = "https://www.metal-archives.com/band/read-more/id/{}"

        # make the request
        r = cls.API_SESSION.get(endpoint.format(ma_artist_id))
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {endpoint.format(ma_artist_id)}")
            return artist

        artist.notes.html = r.text
        return artist

    @classmethod
    def fetch_artist_details(cls, artist: Artist, flat: bool = False) -> Artist:
        source_list = artist.source_collection.get_sources_from_page(cls.SOURCE_TYPE)
        if len(source_list) == 0:
            return artist

        # taking the fist source, cuz I only need one and multiple sources don't make that much sense
        source = source_list[0]
        artist_id = source.url.split("/")[-1]

        """
        TODO
        [x] https://www.metal-archives.com/bands/Ghost_Bath/3540372489
        [x] https://www.metal-archives.com/band/discography/id/3540372489/tab/all
        [] reviews: https://www.metal-archives.com/review/ajax-list-band/id/3540372489/json/1?sEcho=1&iColumns=4&sColumns=&iDisplayStart=0&iDisplayLength=200&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&iSortCol_0=3&sSortDir_0=desc&iSortingCols=1&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&_=1675155257133
        [] simmilar: https://www.metal-archives.com/band/ajax-recommendations/id/3540372489
        [x] sources: https://www.metal-archives.com/link/ajax-list/type/band/id/3540372489
        [x] band notes: https://www.metal-archives.com/band/read-more/id/3540372489
        """

        # SIMPLE METADATA
        artist = cls.fetch_artist_attributes(artist, source.url)

        # DISCOGRAPHY
        artist = cls.fetch_artist_discography(artist, artist_id, flat=flat)

        # EXTERNAL SOURCES
        artist = cls.fetch_artist_sources(artist, artist_id)

        # ARTIST NOTES
        artist = cls.fetch_band_notes(artist, artist_id)

        return artist

    @classmethod
    def fetch_album_details(cls, album: Album, flat: bool = False) -> Album:
        source_list = album.source_collection.get_sources_from_page(cls.SOURCE_TYPE)
        if len(source_list) == 0:
            return album
        
        source = source_list[0]
        album_id = source.url.split("/")[-1]

        # <table class="display table_lyrics

        r = cls.API_SESSION.get(source.url)
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {source.url}")
            return album

        soup = BeautifulSoup(r.text, 'html.parser')

        tracklist_soup = soup.find("table", {"class": "table_lyrics"}).find("tbody")

        for row in tracklist_soup.find_all("tr", {"class": ["even", "odd"]}):
            """
            example of row:
                        
            <tr class="even">
                <td width="20"><a class="anchor" name="5948442"> </a>1.</td>        # id and tracksort
                <td class="wrapWords">Convince Me to Bleed</td>                     # name
                <td align="right">03:40</td>                                        # length
                <td nowrap="nowrap"> 
                <a href="#5948442" id="lyricsButton5948442" onclick="toggleLyrics('5948442'); return false;">Show lyrics</a>
                </td>
            </tr>
            """
            row_list = row.find_all(recursive=False)

            track_sort_soup = row_list[0]
            track_sort = int(track_sort_soup.text[:-1])
            track_id = track_sort_soup.find("a").get("name")

            title = row_list[1].text.strip()
            
            length = None

            duration_stamp = row_list[2].text
            if ":" in duration_stamp:
                minutes, seconds = duration_stamp.split(":")
                length = (int(minutes) * 60 + int(seconds))*1000 # in milliseconds

            album.song_collection.append(
                Song(
                    id_=track_id,
                    title=title,
                    length=length,
                    tracksort=track_sort,
                    source_list=[Source(cls.SOURCE_TYPE, track_id)]
                )
            )

        return album

    @classmethod
    def fetch_song_details(cls, song: Song, flat: bool = False) -> Song:
        source_list = song.source_collection.get_sources_from_page(cls.SOURCE_TYPE)
        if len(source_list) == 0:
            return song

        """
        TODO
        lyrics
        """

        return song
