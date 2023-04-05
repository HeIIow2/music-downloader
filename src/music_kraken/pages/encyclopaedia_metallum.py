from collections import defaultdict
from typing import List, Optional, Dict, Type, Union
import requests
from bs4 import BeautifulSoup
import pycountry
from urllib.parse import urlparse

from ..utils.shared import ENCYCLOPAEDIA_METALLUM_LOGGER
from ..utils import string_processing
from .abstract import Page
from ..objects import (
    Lyrics,
    Artist,
    Source,
    SourcePages,
    Song,
    Album,
    ID3Timestamp,
    FormattedText,
    Label,
    Options,
    AlbumType
)


class EncyclopaediaMetallum(Page):
    API_SESSION: requests.Session = requests.Session()
    API_SESSION.headers = {
        "Host": "www.metal-archives.com",
        "Connection": "keep-alive"
    }

    SOURCE_TYPE = SourcePages.ENCYCLOPAEDIA_METALLUM

    ALBUM_TYPE_MAP: Dict[str, AlbumType] = defaultdict(lambda: AlbumType.OTHER, {
        "Full-length": AlbumType.STUDIO_ALBUM,
        "Single": AlbumType.SINGLE,
        "EP": AlbumType.EP,
        "Demo": AlbumType.DEMO,
        "Video": AlbumType.OTHER,
        "Live album": AlbumType.LIVE_ALBUM,
        "Compilation": AlbumType.COMPILATION_ALBUM
    })
    
    LOGGER = ENCYCLOPAEDIA_METALLUM_LOGGER

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

        r = cls.get_request(endpoint.format(song=query.song_str, artist=query.artist_str, album=query.album_str))
        if r.status_code != 200:
            cls.LOGGER.warning(
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

        r = cls.get_request(endpoint.format(artist=query.artist_str, album=query.album_str))
        if r.status_code != 200:
            cls.LOGGER.warning(
                f"code {r.status_code} at {endpoint.format(song=query.song_str, artist=query.artist_str, album=query.album_str)}")
            return []

        return [cls.get_album_from_json(
            artist_html=raw_album[0],
            album_html=raw_album[1],
            release_type=raw_album[2]
        ) for raw_album in r.json()['aaData']]

    @classmethod
    def search_for_artist(cls, query: Page.Query) -> List[Artist]:
        endpoint = "https://www.metal-archives.com/search/ajax-advanced/searching/bands/?bandName={" \
                   "artist}&genre=&country=&yearCreationFrom=&yearCreationTo=&bandNotes=&status=&themes=&location" \
                   "=&bandLabelName=&sEcho=1&iColumns=3&sColumns=&iDisplayStart=0&iDisplayLength=200&mDataProp_0=0" \
                   "&mDataProp_1=1&mDataProp_2=2&_=1674565459976"

        r = cls.get_request(endpoint.format(artist=query.artist))

        if r is None:
            return []

        data_key = 'aaData'
        parsed_data = r.json()
        if data_key not in parsed_data:
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

        r = cls.get_request(endpoint.format(query=query))
        if r is None:
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

        anchor.decompose()
        strong = soup.find('strong')
        if strong is not None:
            strong.decompose()
            akronyms_ = soup.text[2:-2].split(', ')

        return Artist(
            name=artist_name,
            source_list=[
                Source(SourcePages.ENCYCLOPAEDIA_METALLUM, artist_url)
            ]
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
        
        album_type = cls.ALBUM_TYPE_MAP[release_type.strip()]
        
        return Album(
            title=album_name,
            album_type=album_type,
            source_list=[
                Source(SourcePages.ENCYCLOPAEDIA_METALLUM, album_url)
            ],
            artist_list=[
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
            title=title,
            main_artist_list=[
                cls.get_artist_from_json(artist_html=artist_html)
            ],
            album_list=[
                cls.get_album_from_json(album_html=album_html, release_type=release_type, artist_html=artist_html)
            ],
            source_list=[
                Source(SourcePages.ENCYCLOPAEDIA_METALLUM, song_id)
            ]
        )

    @classmethod
    def _fetch_artist_discography(cls, ma_artist_id: str) -> List[Album]:
        discography_url = "https://www.metal-archives.com/band/discography/id/{}/tab/all"

        # make the request
        r = cls.get_request(discography_url.format(ma_artist_id))
        if r is None:
            return []
        soup = cls.get_soup_from_response(r)

        discography = []

        tbody_soup = soup.find('tbody')
        for tr_soup in tbody_soup.find_all('tr'):
            td_list = tr_soup.findChildren(recursive=False)

            album_soup = td_list[0]
            album_name = album_soup.text
            album_url = album_soup.find('a').get('href')
            album_id = album_url.split('/')[-1]
            raw_album_type = td_list[1].text
            album_year = td_list[2].text
            date_obj = None
            try:
                date_obj = ID3Timestamp(year=int(album_year))
            except ValueError():
                pass

            discography.append(
                Album(
                    title=album_name,
                    date=date_obj,
                    album_type=cls.ALBUM_TYPE_MAP[raw_album_type],
                    source_list=[Source(SourcePages.ENCYCLOPAEDIA_METALLUM, album_url)]
                )
            )

        return discography

    @classmethod
    def _fetch_artist_sources(cls, ma_artist_id: str) -> List[Source]:
        sources_url = "https://www.metal-archives.com/link/ajax-list/type/band/id/{}"
        r = cls.get_request(sources_url.format(ma_artist_id))
        if r is None:
            return []

        soup = cls.get_soup_from_response(r)

        if soup.find("span", {"id": "noLinks"}) is not None:
            return []

        artist_source = soup.find("div", {"id": "band_links_Official"})
        """
        TODO
        add a Label object to add the label sources from
        TODO
        maybe do merchandice stuff
        """
        merchandice_source = soup.find("div", {"id": "band_links_Official_merchandise"})
        label_source = soup.find("div", {"id": "band_links_Labels"})

        source_list = []

        if artist_source is not None:
            for tr in artist_source.find_all("td"):
                a = tr.find("a")
                url = a.get("href")
                if url is None:
                    continue

                source_list.append(Source.match_url(url))

        return source_list

    @classmethod
    def _parse_artist_attributes(cls, artist_soup: BeautifulSoup) -> Artist:
        name: str = None
        country: pycountry.Countrie = None
        formed_in_year: int = None
        genre: str = None
        lyrical_themes: List[str] = []
        label_name: str = None
        label_url: str = None
        source_list: List[Source] = []

        title_soup: BeautifulSoup = artist_soup.find("title")
        if title_soup is not None:
            bad_name_substring = " - Encyclopaedia Metallum: The Metal Archives"
            title_text = title_soup.get_text()
            if title_text.count(bad_name_substring) == 1:
                name = title_text.replace(bad_name_substring, "")
            else:
                cls.LOGGER.debug(f"the title of the page is \"{title_text}\"")

        """
        TODO
        Implement the bandpictures and logos that can be gotten with the elements
        <a class="image" id="photo" title="Ghost Bath"...
        <a class="image" id="logo" title="Ghost Bath"...
        where the titles are the band name
        """
        image_container_soup: BeautifulSoup = artist_soup.find(id="band_sidebar")
        if image_container_soup is not None:
            logo_soup = image_container_soup.find(id="logo")
            if logo_soup is not None:
                logo_title = logo_soup.get("title")
                if logo_title is not None:
                    name = logo_title.strip()

            band_pictures = image_container_soup.find(id="photo")
            if band_pictures is not None:
                band_picture_title = logo_soup.get("title")
                if band_picture_title is not None:
                    name = band_picture_title.strip()

        for h1_band_name_soup in artist_soup.find_all("h1", {"class": "band_name"}):
            anchor: BeautifulSoup = h1_band_name_soup.find("a")
            if anchor is None:
                continue

            href = anchor.get("href")
            if href is not None:
                source_list.append(Source(cls.SOURCE_TYPE, href))

            name = anchor.get_text(strip=True)

        band_stat_soup = artist_soup.find("div", {"id": "band_stats"})
        for dl_soup in band_stat_soup.find_all("dl"):
            for title, data in zip(dl_soup.find_all("dt"), dl_soup.find_all("dd")):
                title_text = title.text

                if "Country of origin:" == title_text:
                    href = data.find('a').get('href')
                    country = pycountry.countries.get(alpha_2=href.split("/")[-1])
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
                    continue
                if "Genre:" == title_text:
                    genre = data.text
                    continue
                if "Lyrical themes:" == title_text:
                    lyrical_themes = data.text.split(", ")
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

                """
                TODO
                years active: 2012-present
                process this and add field to class
                """

        return Artist(
            name=name,
            country=country,
            formed_in=ID3Timestamp(year=formed_in_year),
            general_genre=genre,
            lyrical_themes=lyrical_themes,
            label_list=[
                Label(
                    name=label_name,
                    source_list=[
                        Source(cls.SOURCE_TYPE, label_url)
                    ]
                )
            ],
            source_list=source_list
        )

    @classmethod
    def _fetch_artist_attributes(cls, url: str) -> Artist:
        r = cls.get_request(url)
        if r is None:
            return Artist()
        soup: BeautifulSoup = cls.get_soup_from_response(r)

        return cls._parse_artist_attributes(artist_soup=soup)

    @classmethod
    def _fetch_band_notes(cls, ma_artist_id: str) -> Optional[FormattedText]:
        endpoint = "https://www.metal-archives.com/band/read-more/id/{}"

        # make the request
        r = cls.get_request(endpoint.format(ma_artist_id))
        if r is None:
            return FormattedText()

        return FormattedText(html=r.text)

    @classmethod
    def _fetch_artist_from_source(cls, source: Source, stop_at_level: int = 1) -> Artist:
        """
        What it could fetch, and what is implemented:

        [x] https://www.metal-archives.com/bands/Ghost_Bath/3540372489
        [x] https://www.metal-archives.com/band/discography/id/3540372489/tab/all
        [] reviews: https://www.metal-archives.com/review/ajax-list-band/id/3540372489/json/1?sEcho=1&iColumns=4&sColumns=&iDisplayStart=0&iDisplayLength=200&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&iSortCol_0=3&sSortDir_0=desc&iSortingCols=1&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&_=1675155257133
        [] simmilar: https://www.metal-archives.com/band/ajax-recommendations/id/3540372489
        [x] sources: https://www.metal-archives.com/link/ajax-list/type/band/id/3540372489
        [x] band notes: https://www.metal-archives.com/band/read-more/id/3540372489
        """

        artist = cls._fetch_artist_attributes(source.url)

        artist_id = source.url.split("/")[-1]

        artist_sources = cls._fetch_artist_sources(artist_id)
        artist.source_collection.extend(artist_sources)

        band_notes = cls._fetch_band_notes(artist_id)
        if band_notes is not None:
            artist.notes = band_notes

        discography: List[Album] = cls._fetch_artist_discography(artist_id)
        if stop_at_level > 1:
            for album in discography:
                for source in album.source_collection.get_sources_from_page(cls.SOURCE_TYPE):
                    album.merge(cls._fetch_album_from_source(source, stop_at_level=stop_at_level-1))
        artist.main_album_collection.extend(discography)

        return artist

    @classmethod
    def _parse_album_track_row(cls, track_row: BeautifulSoup) -> Song:
        """
        <tr class="even">
            <td width="20"><a class="anchor" name="5948442"> </a>1.</td>        # id and tracksort
            <td class="wrapWords">Convince Me to Bleed</td>                     # name
            <td align="right">03:40</td>                                        # length
            <td nowrap="nowrap"> 
            <a href="#5948442" id="lyricsButton5948442" onclick="toggleLyrics('5948442'); return false;">Show lyrics</a>
            </td>
        </tr>
        """
        
        row_list = track_row.find_all(recursive=False)

        source_list: List[Source] = []

        track_sort_soup = row_list[0]
        track_sort = int(track_sort_soup.text[:-1])
        track_id = track_sort_soup.find("a").get("name").strip()
        
        if track_row.find("a", {"href": f"#{track_id}"}) is not None:
            source_list.append(Source(cls.SOURCE_TYPE, track_id))

        title = row_list[1].text.strip()

        length = None

        duration_stamp = row_list[2].text
        if ":" in duration_stamp:
            minutes, seconds = duration_stamp.split(":")
            length = (int(minutes) * 60 + int(seconds)) * 1000  # in milliseconds

        return Song(
            title=title,
            length=length,
            tracksort=track_sort,
            source_list=source_list
        )
        

    @classmethod
    def _parse_album_attributes(cls, album_soup: BeautifulSoup, stop_at_level: int = 1) -> Album:
        tracklist: List[Song] = []
        artist_list = []
        album_name: str = None
        source_list: List[Source] = []
        
        def _parse_album_info(album_info_soup: BeautifulSoup):
            nonlocal artist_list
            nonlocal album_name
            nonlocal source_list
            
            if album_info_soup is None:
                return
            
            album_soup_list = album_info_soup.find_all("h1", {"class": "album_name"})
            if len(album_soup_list) == 1:
                anchor: BeautifulSoup = album_soup_list[0].find("a")
                
                href = anchor.get("href")
                if href is not None:
                    source_list.append(Source(cls.SOURCE_TYPE, href.strip()))
                    
                album_name = anchor.get_text(strip=True)
                
            elif len(album_soup_list) > 1:
                cls.LOGGER.debug("there are more than 1 album soups")
                
            
            artist_soup_list = album_info_soup.find_all("h2", {"class": "band_name"})
            if len(artist_soup_list) == 1:
                for anchor in artist_soup_list[0].find_all("a"):
                    artist_sources: List[Source] = []
                    
                    href = anchor.get("href")
                    if href is not None:
                        artist_sources.append(Source(cls.SOURCE_TYPE, href.strip()))
                        
                    artist_name = anchor.get_text(strip=True)
                    
                    artist_list.append(Artist(
                        name=artist_name,
                        source_list=artist_sources
                    ))
                
            elif len(artist_soup_list) > 1:
                cls.LOGGER.debug("there are more than 1 artist soups")
        
        _parse_album_info(album_info_soup=album_soup.find(id="album_info"))
        
        tracklist_soup = album_soup.find("table", {"class": "table_lyrics"}).find("tbody")
        for track_soup in tracklist_soup.find_all("tr", {"class": ["even", "odd"]}):
            tracklist.append(cls._parse_album_track_row(track_row=track_soup))

        return Album(
            title=album_name,
            source_list=source_list,
            artist_list=artist_list,
            song_list=tracklist
        )

    @classmethod
    def _fetch_album_from_source(cls, source: Source, stop_at_level: int = 1) -> Album:
        """
        I am preeeety sure I can get way more data than... nothing from there

        :param source:
        :param stop_at_level:
        :return:
        """

        # <table class="display table_lyrics

        r = cls.get_request(source.url)
        if r is None:
            return Album()

        soup = cls.get_soup_from_response(r)
        
        album = cls._parse_album_attributes(soup, stop_at_level=stop_at_level)
        
        if stop_at_level > 1:
            for song in album.song_collection:
                for source in song.source_collection.get_sources_from_page(cls.SOURCE_TYPE):
                    song.merge(cls._fetch_song_from_source(source=source, stop_at_level=stop_at_level-1))
                    
        return album
    
    @classmethod
    def _fetch_lyrics(cls, song_id: str) -> Optional[Lyrics]:
        """
        function toggleLyrics(songId) {
            var lyricsRow = $('#song' + songId);
            lyricsRow.toggle();
            var lyrics = $('#lyrics_' + songId);
            if (lyrics.html() == '(loading lyrics...)') {
                var realId = songId;
                if(!$.isNumeric(songId.substring(songId.length -1, songId.length))) {
                    realId = songId.substring(0, songId.length -1);
                }
                lyrics.load(URL_SITE + "release/ajax-view-lyrics/id/" + realId);
            }
            // toggle link
            var linkLabel = "lyrics";
            $("#lyricsButton" + songId).text(lyricsRow.css("display") == "none" ? "Show " + linkLabel : "Hide " + linkLabel);
            return false;
        }
        """
        if song_id is None:
            return None
        
        endpoint = "https://www.metal-archives.com/release/ajax-view-lyrics/id/{id}".format(id=song_id)
        
        r = cls.get_request(endpoint)
        if r is None:
            return None
        
        return Lyrics(
            text=FormattedText(html=r.text),
            language=pycountry.languages.get(alpha_2="en"),
            source_list=[
                Source(cls.SOURCE_TYPE, endpoint)
            ]
        )

    @classmethod
    def _fetch_song_from_source(cls, source: Source, stop_at_level: int = 1) -> Song:
        song_id = source.url
        
        return Song(
            lyrics_list=[
                cls._fetch_lyrics(song_id=song_id)
            ]
        )

    @classmethod
    def _get_type_of_url(cls, url: str) -> Optional[Union[Type[Song], Type[Album], Type[Artist], Type[Label]]]:
        parsed_url = urlparse(url)
        path: List[str] = parsed_url.path.split("/")
        
        if "band" in path:
            return Artist
        if "bands" in path:
            return Artist
        
        if "albums" in path:
            return Album
        
        if "labels" in path:
            return Label
        
        return None
