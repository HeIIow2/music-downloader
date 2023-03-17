from collections import defaultdict
from typing import List, Optional, Union
import requests
from bs4 import BeautifulSoup
import pycountry
import time
from urllib.parse import urlparse
from enum import Enum
from dataclasses import dataclass

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
    Options,
    AlbumType,
    AlbumStatus
)
from ..utils import (
    string_processing,
    shared
)
from ..utils.shared import (
    MUSIFY_LOGGER as LOGGER
)

"""
https://musify.club/artist/ghost-bath-280348?_pjax=#bodyContent
https://musify.club/artist/ghost-bath-280348/releases?_pjax=#bodyContent
https://musify.club/artist/ghost-bath-280348/clips?_pjax=#bodyContent
https://musify.club/artist/ghost-bath-280348/photos?_pjax=#bodyContent

POST https://musify.club/artist/filtersongs
ID: 280348
NameForUrl: ghost-bath
Page: 1
IsAllowed: True
SortOrder.Property: dateCreated
SortOrder.IsAscending: false
X-Requested-With: XMLHttpRequest

POST https://musify.club/artist/filteralbums
ArtistID: 280348
SortOrder.Property: dateCreated
SortOrder.IsAscending: false
X-Requested-With: XMLHttpRequest
"""


class MusifyTypes(Enum):
    ARTIST = "artist"


@dataclass
class MusifyUrl:
    source_type: MusifyTypes
    name_without_id: str
    name_with_id: str
    musify_id: str
    url: str


class Musify(Page):
    API_SESSION: requests.Session = requests.Session()
    API_SESSION.headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Connection": "keep-alive",
        "Referer": "https://musify.club/"
    }
    API_SESSION.proxies = shared.proxies
    TIMEOUT = 5
    TRIES = 5
    HOST = "https://musify.club"

    SOURCE_TYPE = SourcePages.MUSIFY

    @classmethod
    def search_by_query(cls, query: str) -> Options:
        query_obj = cls.Query(query)

        if query_obj.is_raw:
            return cls.plaintext_search(query_obj.query)
        return cls.plaintext_search(cls.get_plaintext_query(query_obj))

    @classmethod
    def get_plaintext_query(cls, query: Page.Query) -> str:
        if query.album is None:
            return f"{query.artist or '*'} - {query.song or '*'}"
        return f"{query.artist or '*'} - {query.album or '*'} - {query.song or '*'}"

    @classmethod
    def parse_artist_contact(cls, contact: BeautifulSoup) -> Artist:
        source_list: List[Source] = []
        name = ""
        _id = None

        # source
        anchor = contact.find("a")
        if anchor is not None:
            href = anchor.get("href")
            name = anchor.get("title")

            if "-" in href:
                _id = href.split("-")[-1]

            source_list.append(Source(cls.SOURCE_TYPE, cls.HOST + href))

        # artist image
        image_soup = contact.find("img")
        if image_soup is not None:
            alt = image_soup.get("alt")
            if alt is not None:
                name = alt

            artist_thumbnail = image_soup.get("src")

        return Artist(
            _id=_id,
            name=name,
            source_list=source_list
        )

    @classmethod
    def parse_album_contact(cls, contact: BeautifulSoup) -> Album:
        """
        <div class="contacts__item">
            <a href="/release/ghost-bath-ghost-bath-2013-602489" title="Ghost Bath - 2013">
            
            <div class="contacts__img release">
                <img alt="Ghost Bath" class="lozad" data-src="https://37s.musify.club/img/69/9060265/24178833.jpg"/>
                <noscript><img alt="Ghost Bath" src="https://37s.musify.club/img/69/9060265/24178833.jpg"/></noscript>
            </div>
            
            <div class="contacts__info">
                <strong>Ghost Bath - 2013</strong>
                <small>Ghost Bath</small>
                <small>Треков: 4</small>    <!--tracks-->
                <small><i class="zmdi zmdi-star zmdi-hc-fw"></i> 9,04</small>
            </div>
            </a>
        </div>
        """

        source_list: List[Source] = []
        title = ""
        _id = None
        year = None
        artist_list: List[Artist] = []

        def parse_title_date(title_date: Optional[str], delimiter: str = " - "):
            if title_date is None:
                return

            title_date = title_date.strip()
            split_attr = title_date.split(delimiter)

            if len(split_attr) < 2:
                return
            if not split_attr[-1].isdigit():
                return

            year = int(split_attr[-1])
            title = delimiter.join(split_attr[:-1])

        # source
        anchor = contact.find("a")
        if anchor is not None:
            href = anchor.get("href")

            # get the title and year
            parse_title_date(anchor.get("title"))

            if "-" in href:
                _id = href.split("-")[-1]

            source_list.append(Source(cls.SOURCE_TYPE, cls.HOST + href))

        # cover art
        image_soup = contact.find("img")
        if image_soup is not None:
            alt = image_soup.get("alt")
            if alt is not None:
                title = alt

            cover_art = image_soup.get("src")

        contact_info_soup = contact.find("div", {"class": "contacts__info"})
        if contact_info_soup is not None:
            """
            <strong>Ghost Bath - 2013</strong>
            <small>Ghost Bath</small>
            <small>Треков: 4</small>    <!--tracks-->
            <small><i class="zmdi zmdi-star zmdi-hc-fw"></i> 9,04</small>
            """

            title_soup = contact_info_soup.find("strong")
            if title_soup is None:
                parse_title_date(title_soup)

            small_list = contact_info_soup.find_all("small")
            if len(small_list) == 3:
                # artist
                artist_soup: BeautifulSoup = small_list[0]
                raw_artist_str = artist_soup.text

                for artist_str in raw_artist_str.split("&\r\n"):
                    artist_str = artist_str.rstrip("& ...\r\n")
                    artist_str = artist_str.strip()

                    if artist_str.endswith("]") and "[" in artist_str:
                        artist_str = artist_str.rsplit("[", maxsplit=1)[0]

                    artist_list.append(Artist(name=artist_str))

                track_count_soup: BeautifulSoup = small_list[1]
                rating_soup: BeautifulSoup = small_list[2]
            else:
                LOGGER.warning("got an unequal ammount than 3 small elements")

        return Album(
            _id=_id,
            title=title,
            source_list=source_list,
            date=ID3Timestamp(year=year),
            artist_list=artist_list
        )

    @classmethod
    def parse_contact_container(cls, contact_container_soup: BeautifulSoup) -> List[Union[Artist, Album]]:
        # print(contact_container_soup.prettify)
        contacts = []

        # print(contact_container_soup)

        contact: BeautifulSoup
        for contact in contact_container_soup.find_all("div", {"class": "contacts__item"}):

            anchor_soup = contact.find("a")

            if anchor_soup is not None:
                url = anchor_soup.get("href")

                if url is not None:
                    # print(url)
                    if "artist" in url:
                        contacts.append(cls.parse_artist_contact(contact))
                    elif "release" in url:
                        contacts.append(cls.parse_album_contact(contact))
        return contacts

    @classmethod
    def parse_playlist_item(cls, playlist_item_soup: BeautifulSoup) -> Song:
        _id = None
        song_title = playlist_item_soup.get("data-name") or ""
        artist_list: List[Artist] = []
        source_list: List[Source] = []

        # details
        playlist_details: BeautifulSoup = playlist_item_soup.find("div", {"class", "playlist__heading"})
        if playlist_details is not None:
            anchor_list = playlist_details.find_all("a")

            if len(anchor_list) >= 2:
                print(anchor_list)
                # artists
                artist_anchor: BeautifulSoup
                for artist_anchor in anchor_list[:-1]:
                    _id = None
                    href = artist_anchor.get("href")
                    artist_source: Source = Source(cls.SOURCE_TYPE, cls.HOST + href)
                    if "-" in href:
                        _id = href.split("-")[-1]

                    artist_list.append(Artist(
                        _id=_id,
                        name=artist_anchor.get_text(strip=True),
                        source_list=[artist_source]
                    ))

                # track
                track_soup: BeautifulSoup = anchor_list[-1]
                """
                TODO
                this anchor text may have something like (feat. some artist)
                which is not acceptable
                """
                href = track_soup.get("href")
                if href is not None:
                    if "-" in href:
                        raw_id: str = href.split("-")[-1]
                        if raw_id.isdigit():
                            _id = raw_id
                    source_list.append(Source(cls.SOURCE_TYPE, cls.HOST + href))

            else:
                LOGGER.warning("there are not enough anchors (2) for artist and track")
                LOGGER.warning(str(artist_list))

        """
        artist_name = playlist_item_soup.get("data-artist")
        if artist_name is not None:
            artist_list.append(Artist(name=artist_name))
        """
        id_attribute = playlist_item_soup.get("id")
        if id_attribute is not None:
            raw_id = id_attribute.replace("playerDiv", "")
            if raw_id.isdigit():
                _id = raw_id

        return Song(
            _id=_id,
            title=song_title,
            main_artist_list=artist_list,
            source_list=source_list
        )

    @classmethod
    def parse_playlist_soup(cls, playlist_soup: BeautifulSoup) -> List[Song]:
        song_list = []

        for playlist_item_soup in playlist_soup.find_all("div", {"class": "playlist__item"}):
            song_list.append(cls.parse_playlist_item(playlist_item_soup))

        return song_list

    @classmethod
    def plaintext_search(cls, query: str) -> Options:
        search_results = []

        r = cls.get_request(f"https://musify.club/search?searchText={query}")
        if r is None:
            return Options()
        search_soup: BeautifulSoup = BeautifulSoup(r.content, features="html.parser")

        # album and songs
        # child of div class: contacts row
        for contact_container_soup in search_soup.find_all("div", {"class": "contacts"}):
            search_results.extend(cls.parse_contact_container(contact_container_soup))

        # song
        # div class: playlist__item
        for playlist_soup in search_soup.find_all("div", {"class": "playlist"}):
            search_results.extend(cls.parse_playlist_soup(playlist_soup))

        return Options(search_results)

    @classmethod
    def parse_url(cls, url: str) -> MusifyUrl:
        parsed = urlparse(url)

        path = parsed.path.split("/")

        split_name = path[2].split("-")
        url_id = split_name[-1]
        name_for_url = "-".join(split_name[:-1])

        return MusifyUrl(
            source_type=MusifyTypes(path[1]),
            name_without_id=name_for_url,
            name_with_id=path[2],
            musify_id=url_id,
            url=url
        )

    @classmethod
    def parse_album_card(cls, album_card: BeautifulSoup) -> Album:
        """
        <div class="card release-thumbnail" data-type="2">
            <a href="/release/ghost-bath-self-loather-2021-1554266">
                <img alt="Self Loather" class="card-img-top lozad" data-src="https://40s-a.musify.club/img/70/24826582/62624396.jpg"/>
                <noscript><img alt="Self Loather" src="https://40s-a.musify.club/img/70/24826582/62624396.jpg"/></noscript>
            </a>
            <div class="card-body">
                <h4 class="card-subtitle">
                <a href="/release/ghost-bath-self-loather-2021-1554266">Self Loather</a>
                </h4>
            </div>
            <div class="card-footer"><p class="card-text"><a href="/albums/2021">2021</a></p></div>
            <div class="card-footer">
                <p class="card-text genre__labels">
                <a href="/genre/depressive-black-132">Depressive Black</a><a href="/genre/post-black-metal-295">Post-Black Metal</a> </p>
            </div>
            <div class="card-footer">
                <small><i class="zmdi zmdi-calendar" title="Добавлено"></i> 13.11.2021</small>
                <small><i class="zmdi zmdi-star zmdi-hc-fw" title="Рейтинг"></i> 5,88</small>
            </div>
        </div>
        """

        album_type_map = defaultdict(lambda: AlbumType.OTHER, {
            1: AlbumType.OTHER,                 # literally other xD
            2: AlbumType.STUDIO_ALBUM,
            3: AlbumType.EP,
            4: AlbumType.SINGLE,
            5: AlbumType.OTHER,                 # BOOTLEG
            6: AlbumType.LIVE_ALBUM,
            7: AlbumType.COMPILATION_ALBUM,     # compilation of different artists
            8: AlbumType.MIXTAPE,
            9: AlbumType.DEMO,
            10: AlbumType.MIXTAPE,              # DJ Mixes
            11: AlbumType.COMPILATION_ALBUM,    # compilation of only this artist
            13: AlbumType.COMPILATION_ALBUM,    # unofficial
            14: AlbumType.MIXTAPE               # "Soundtracks"
        })

        _id: Optional[str] = None
        name: str = ""
        source_list: List[Source] = []
        timestamp: Optional[ID3Timestamp] = None
        album_status = None

        album_status_id = album_card.get("data-type")
        if album_status_id.isdigit():
            album_status_id = int(album_status_id)
        album_type = album_type_map[album_status_id]

        if album_status_id == 5:
            album_status = AlbumStatus.BOOTLEG

        def parse_release_anchor(_anchor: BeautifulSoup, text_is_name=False):
            nonlocal _id
            nonlocal name
            nonlocal source_list

            if _anchor is None:
                return

            href = _anchor.get("href")
            if href is not None:
                # add url to sources
                source_list.append(Source(
                    cls.SOURCE_TYPE,
                    cls.HOST + href
                ))

                # split id from url
                split_href = href.split("-")
                if len(split_href) > 1:
                    _id = split_href[-1]

            if not text_is_name:
                return

            name = _anchor.text

        anchor_list = album_card.find_all("a", recursive=False)
        if len(anchor_list) > 0:
            anchor = anchor_list[0]
            parse_release_anchor(anchor)

            thumbnail: BeautifulSoup = anchor.find("img")
            if thumbnail is not None:
                alt = thumbnail.get("alt")
                if alt is not None:
                    name = alt

                image_url = thumbnail.get("src")
        else:
            LOGGER.debug("the card has no thumbnail or url")

        card_body = album_card.find("div", {"class": "card-body"})
        if card_body is not None:
            parse_release_anchor(card_body.find("a"), text_is_name=True)

        def parse_small_date(small_soup: BeautifulSoup):
            """
            <small>
                <i class="zmdi zmdi-calendar" title="Добавлено"></i>
                13.11.2021
            </small>
            """
            nonlocal timestamp

            italic_tagging_soup: BeautifulSoup = small_soup.find("i")
            if italic_tagging_soup is None:
                return
            if italic_tagging_soup.get("title") != "Добавлено":
                # "Добавлено" can be translated to "Added (at)"
                return

            raw_time = small_soup.text.strip()
            timestamp = ID3Timestamp.strptime(raw_time, "%d.%m.%Y")

        # parse small date
        card_footer_list = album_card.find_all("div", {"class": "card-footer"})
        if len(card_footer_list) != 3:
            LOGGER.debug("there are not exactly 3 card footers in a card")

        if len(card_footer_list) > 0:
            for any_small_soup in card_footer_list[-1].find_all("small"):
                parse_small_date(any_small_soup)
        else:
            LOGGER.debug("there is not even 1 footer in the album card")

        return Album(
            _id=_id,
            title=name,
            source_list=source_list,
            date=timestamp,
            album_type=album_type,
            album_status=album_status
        )

    @classmethod
    def get_discography(cls, url: MusifyUrl) -> List[Album]:
        """
        POST https://musify.club/artist/filteralbums
        ArtistID: 280348
        SortOrder.Property: dateCreated
        SortOrder.IsAscending: false
        X-Requested-With: XMLHttpRequest
        """

        endpoint = cls.HOST + "/" + url.source_type.value + "/filteralbums"

        r = cls.post_request(url=endpoint, json={
            "ArtistID": str(url.musify_id),
            "SortOrder.Property": "dateCreated",
            "SortOrder.IsAscending": False,
            "X-Requested-With": "XMLHttpRequest"
        })
        if r is None:
            return []
        soup: BeautifulSoup = BeautifulSoup(r.content, features="html.parser")

        discography: List[Album] = []
        for card_soup in soup.find_all("div", {"class": "card"}):
            discography.append(cls.parse_album_card(card_soup))

        return discography

    @classmethod
    def get_artist_attributes(cls, url: MusifyUrl) -> Artist:
        """
        fetches the main Artist attributes from this endpoint
        https://musify.club/artist/ghost-bath-280348?_pjax=#bodyContent
        it needs to parse html

        :param url:
        :return:
        """
        return Artist(
            name=""
        )

    @classmethod
    def get_artist_from_source(cls, source: Source, flat: bool = False) -> Artist:
        """
        fetches artist from source

        [x] discography
        [] attributes
        [] picture galery

        Args:
            source (Source): the source to fetch
            flat (bool, optional): if it is false, every album from discograohy will be fetched. Defaults to False.

        Returns:
            Artist: the artist fetched
        """

        url = cls.parse_url(source.url)

        artist = cls.get_artist_attributes(url)

        discography: List[Album] = cls.get_discography(url)
        artist.main_album_collection.extend(discography)

        return artist

    @classmethod
    def fetch_artist_details(cls, artist: Artist, flat: bool = False) -> Artist:
        source_list = artist.source_collection.get_sources_from_page(cls.SOURCE_TYPE)
        if len(source_list) == 0:
            return artist

        for source in source_list:
            artist.merge(cls.get_artist_from_source(source, flat=flat))

        return artist

    @classmethod
    def fetch_album_details(cls, album: Album, flat: bool = False) -> Album:

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
