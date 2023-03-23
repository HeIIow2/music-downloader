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
    RELEASE = "release"
    SONG = "track"


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
    def parse_url(cls, url: str) -> MusifyUrl:
        parsed = urlparse(url)

        path = parsed.path.split("/")

        split_name = path[2].split("-")
        url_id = split_name[-1]
        name_for_url = "-".join(split_name[:-1])

        try:
            type_enum = MusifyTypes(path[1])
        except ValueError as e:
            print(f"{path[1]} is not yet implemented, add it to MusifyTypes")
            raise e

        return MusifyUrl(
            source_type=type_enum,
            name_without_id=name_for_url,
            name_with_id=path[2],
            musify_id=url_id,
            url=url
        )

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
        name = None
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
        title = None
        _id = None
        year = None
        artist_list: List[Artist] = []

        def parse_title_date(title_date: Optional[str], delimiter: str = " - "):
            nonlocal year
            nonlocal title

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

        return cls.ALBUM_CACHE.append(Album(
            _id=_id,
            title=title,
            source_list=source_list,
            date=ID3Timestamp(year=year),
            artist_list=artist_list
        ))

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
        song_title = playlist_item_soup.get("data-name")
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
    def parse_album_card(cls, album_card: BeautifulSoup, artist_name: str = None) -> Album:
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
        name: str = None
        source_list: List[Source] = []
        timestamp: Optional[ID3Timestamp] = None
        album_status = None

        def set_name(new_name: str):
            nonlocal name
            nonlocal artist_name
            
            # example of just setting not working: https://musify.club/release/unjoy-eurythmie-psychonaut-4-tired-numb-still-alive-2012-324067
            if new_name.count(" - ") != 1:
                name = new_name
                return
            
            potential_artist_list, potential_name = new_name.split(" - ")
            unified_artist_list = string_processing.unify(potential_artist_list)
            if artist_name is not None:
                if string_processing.unify(artist_name) not in unified_artist_list:
                    name = new_name
                    return
                
                name = potential_name
                return
            
            name = new_name

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

            set_name(_anchor.text)

        anchor_list = album_card.find_all("a", recursive=False)
        if len(anchor_list) > 0:
            anchor = anchor_list[0]
            parse_release_anchor(anchor)

            thumbnail: BeautifulSoup = anchor.find("img")
            if thumbnail is not None:
                alt = thumbnail.get("alt")
                if alt is not None:
                    set_name(alt)

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

        return cls.ALBUM_CACHE.append(Album(
            _id=_id,
            title=name,
            source_list=source_list,
            date=timestamp,
            album_type=album_type,
            album_status=album_status
        ))

    @classmethod
    def get_discography(cls, url: MusifyUrl, artist_name: str = None, flat=False) -> List[Album]:
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
            new_album: Album = cls.parse_album_card(card_soup, artist_name)
            album_source: Source
            if not flat:
                for album_source in new_album.source_collection.get_sources_from_page(cls.SOURCE_TYPE):
                    new_album.merge(cls.fetch_album_from_source(album_source))
                    
            discography.append(new_album)

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

        r = cls.get_request(f"https://musify.club/{url.source_type.value}/{url.name_with_id}?_pjax=#bodyContent")
        if r is None:
            return Artist(_id=url.musify_id)

        soup = BeautifulSoup(r.content, "html.parser")

        """
        <ol class="breadcrumb" itemscope="" itemtype="http://schema.org/BreadcrumbList">
            <li class="breadcrumb-item" itemprop="itemListElement" itemscope="" itemtype="http://schema.org/ListItem"><a href="/" itemprop="item"><span itemprop="name">Главная</span><meta content="1" itemprop="position"/></a></li>
            <li class="breadcrumb-item" itemprop="itemListElement" itemscope="" itemtype="http://schema.org/ListItem"><a href="/artist" itemprop="item"><span itemprop="name">Исполнители</span><meta content="2" itemprop="position"/></a></li>
            <li class="breadcrumb-item active">Ghost Bath</li>
        </ol>
        
        <ul class="nav nav-tabs nav-fill">
            <li class="nav-item"><a class="active nav-link" href="/artist/ghost-bath-280348">песни (41)</a></li>
            <li class="nav-item"><a class="nav-link" href="/artist/ghost-bath-280348/releases">альбомы (12)</a></li>
            <li class="nav-item"><a class="nav-link" href="/artist/ghost-bath-280348/clips">видеоклипы (23)</a></li>
            <li class="nav-item"><a class="nav-link" href="/artist/ghost-bath-280348/photos">фото (38)</a></li>
        </ul>
        
        <header class="content__title">
            <h1>Ghost Bath</h1>
            <div class="actions">
                ...
            </div>
        </header>
        
        <ul class="icon-list">
            <li>
                <i class="zmdi zmdi-globe zmdi-hc-fw" title="Страна"></i> 
                <i class="flag-icon US shadow"></i>
                Соединенные Штаты
            </li>
        </ul>
        """
        name = None
        source_list: List[Source] = []
        country = None
        notes: FormattedText = FormattedText()

        breadcrumbs: BeautifulSoup = soup.find("ol", {"class": "breadcrumb"})
        if breadcrumbs is not None:
            breadcrumb_list: List[BeautifulSoup] = breadcrumbs.find_all("li", {"class": "breadcrumb-item"}, recursive=False)
            if len(breadcrumb_list) == 3:
                name = breadcrumb_list[-1].get_text(strip=True)
            else:
                LOGGER.debug("breadcrumb layout on artist page changed")

        nav_tabs: BeautifulSoup = soup.find("ul", {"class": "nav-tabs"})
        if nav_tabs is not None:
            list_item: BeautifulSoup
            for list_item in nav_tabs.find_all("li", {"class": "nav-item"}, recursive=False):
                if not list_item.get_text(strip=True).startswith("песни"):
                    # "песни" translates to "songs"
                    continue

                anchor: BeautifulSoup = list_item.find("a")
                if anchor is None:
                    continue
                href = anchor.get("href")
                if href is None:
                    continue

                source_list.append(Source(
                    cls.SOURCE_TYPE,
                    cls.HOST + href
                ))

        content_title: BeautifulSoup = soup.find("header", {"class": "content__title"})
        if content_title is not None:
            h1_name: BeautifulSoup = content_title.find("h1", recursive=False)
            if h1_name is not None:
                name = h1_name.get_text(strip=True)

        # country and sources
        icon_list: BeautifulSoup = soup.find("ul", {"class": "icon-list"})
        if icon_list is not None:
            country_italic: BeautifulSoup = icon_list.find("i", {"class", "flag-icon"})
            if country_italic is not None:
                style_classes: set = {'flag-icon', 'shadow'}
                classes: set = set(country_italic.get("class"))

                country_set: set = classes.difference(style_classes)
                if len(country_set) != 1:
                    LOGGER.debug("the country set contains multiple values")
                if len(country_set) != 0:
                    """
                    This is the css file, where all flags that can be used on musify
                    are laid out and styled.
                    Every flag has two upper case letters, thus I assume they follow the alpha_2
                    standard, though I haven't checked.
                    https://musify.club/content/flags.min.css
                    """

                    country = pycountry.countries.get(alpha_2=list(country_set)[0])

            # get all additional sources
            additional_source: BeautifulSoup
            for additional_source in icon_list.find_all("a", {"class", "link"}):
                href = additional_source.get("href")
                if href is None:
                    continue
                new_src = Source.match_url(href)
                if new_src is None:
                    continue
                source_list.append(new_src)

        note_soup: BeautifulSoup = soup.find(id="text-main")
        if note_soup is not None:
            notes.html = note_soup.decode_contents()

        return Artist(
            _id=url.musify_id,
            name=name,
            country=country,
            source_list=source_list,
            notes=notes
        )

    @classmethod
    def fetch_artist_from_source(cls, source: Source, flat: bool = False) -> Artist:
        """
        fetches artist from source

        [x] discography
        [x] attributes
        [] picture gallery

        Args:
            source (Source): the source to fetch
            flat (bool, optional): if it is false, every album from discograohy will be fetched. Defaults to False.

        Returns:
            Artist: the artist fetched
        """

        url = cls.parse_url(source.url)

        artist = cls.get_artist_attributes(url)

        discography: List[Album] = cls.get_discography(url, artist.name)
        artist.main_album_collection.extend(discography)

        return artist

    @classmethod
    def parse_song_card(cls, song_card: BeautifulSoup) -> Song:
        """
            <div id="playerDiv3051" class="playlist__item" itemprop="track" itemscope="itemscope" itemtype="http://schema.org/MusicRecording" data-artist="Linkin Park" data-name="Papercut">
                <div id="play_3051" class="playlist__control play" data-url="/track/play/3051/linkin-park-papercut.mp3" data-position="1" data-title="Linkin Park - Papercut" title="Слушать Linkin Park - Papercut">
                    <span class="ico-play"><i class="zmdi zmdi-play-circle-outline zmdi-hc-2-5x"></i></span>
                    <span class="ico-pause"><i class="zmdi zmdi-pause-circle-outline zmdi-hc-2-5x"></i></span>
                </div>
                <div class="playlist__position">
                    1
                </div>
                <div class="playlist__details">
                    <div class="playlist__heading">
                        <a href="/artist/linkin-park-5" rel="nofollow">Linkin Park</a> - <a class="strong" href="/track/linkin-park-papercut-3051">Papercut</a>
                        <span itemprop="byArtist" itemscope="itemscope" itemtype="http://schema.org/MusicGroup">
                            <meta content="/artist/linkin-park-5" itemprop="url" />
                            <meta content="Linkin Park" itemprop="name" />
                        </span>
                    </div>
                </div>
                <div>
                    <div class="track__details track__rating hidden-xs-down">
                        <span class="text-muted">
                            <i class="zmdi zmdi-star-circle zmdi-hc-1-3x" title="Рейтинг"></i>
                            326,3K
                        </span>
                    </div>
                </div>
                <div class="track__details hidden-xs-down">
                    <span class="text-muted">03:05</span>
                    <span class="text-muted">320 Кб/с</span>
                </div>
                <div class="track__details hidden-xs-down">
                    <span title='Есть видео Linkin Park - Papercut'><i class='zmdi zmdi-videocam zmdi-hc-1-3x'></i></span>
                    <span title='Есть текст Linkin Park - Papercut'><i class='zmdi zmdi-file-text zmdi-hc-1-3x'></i></span>
                </div>
                <div class="playlist__actions">
                    <span class="pl-btn save-to-pl" id="add_3051" title="Сохранить в плейлист"><i class="zmdi zmdi-plus zmdi-hc-1-5x"></i></span>
                    <a target="_blank" itemprop="audio" download="Linkin Park - Papercut.mp3" href="/track/dl/3051/linkin-park-papercut.mp3" class="no-ajaxy yaBrowser" id="dl_3051" title='Скачать Linkin Park - Papercut'>
                        <span><i class="zmdi zmdi-download zmdi-hc-2-5x"></i></span>
                    </a>
                </div>
            </div>
        """
        song_name = song_card.get("data-name")
        artist_list: List[Artist] = []
        source_list: List[Source] = []
        tracksort = None

        def parse_title(_title: str) -> str:
            return _title

        """
        # get from parent div
        _artist_name = song_card.get("data-artist")
        if _artist_name is not None:
            artist_list.append(Artist(name=_artist_name))
        """

        # get tracksort
        tracksort_soup: BeautifulSoup = song_card.find("div", {"class": "playlist__position"})
        if tracksort_soup is not None:
            raw_tracksort: str = tracksort_soup.get_text(strip=True)
            if raw_tracksort.isdigit():
                tracksort = int(raw_tracksort)

        # playlist details
        playlist_details: BeautifulSoup = song_card.find("div", {"class": "playlist__details"})
        if playlist_details is not None:
            """
            <div class="playlist__heading">
                <a href="/artist/tamas-141317" rel="nofollow">Tamas</a> ft.<a href="/artist/zombiez-630767" rel="nofollow">Zombiez</a> - <a class="strong" href="/track/tamas-zombiez-voodoo-feat-zombiez-16185276">Voodoo (Feat. Zombiez)</a>                            
                <span itemprop="byArtist" itemscope="itemscope" itemtype="http://schema.org/MusicGroup">
                    <meta content="/artist/tamas-141317" itemprop="url" />
                    <meta content="Tamas" itemprop="name" />
                </span>
                <span itemprop="byArtist" itemscope="itemscope" itemtype="http://schema.org/MusicGroup">
                    <meta content="/artist/zombiez-630767" itemprop="url" />
                    <meta content="Zombiez" itemprop="name" />
                </span>
            </div>
            """
            # track
            anchor_list: List[BeautifulSoup] = playlist_details.find_all("a")
            if len(anchor_list) > 1:
                track_anchor: BeautifulSoup = anchor_list[-1]
                href: str = track_anchor.get("href")
                if href is not None:
                    source_list.append(Source(cls.SOURCE_TYPE, cls.HOST + href))
                song_name = parse_title(track_anchor.get_text(strip=True))

            # artist
            artist_span: BeautifulSoup
            for artist_span in playlist_details.find_all("span", {"itemprop": "byArtist"}):
                _artist_src = None
                _artist_name = None
                meta_artist_src = artist_span.find("meta", {"itemprop": "url"})
                if meta_artist_src is not None:
                    meta_artist_url = meta_artist_src.get("content")
                    if meta_artist_url is not None:
                        _artist_src = [Source(cls.SOURCE_TYPE, cls.HOST + meta_artist_url)]

                meta_artist_name = artist_span.find("meta", {"itemprop": "name"})
                if meta_artist_name is not None:
                    meta_artist_name_text = meta_artist_name.get("content")
                    _artist_name = meta_artist_name_text

                if _artist_name is not None or _artist_src is not None:
                    artist_list.append(Artist(name=_artist_name, source_list=_artist_src))

        return Song(
            title=song_name,
            tracksort=tracksort,
            main_artist_list=artist_list
        )

    @classmethod
    def fetch_album_from_source(cls, source: Source, flat: bool = False) -> Album:
        """
        fetches album from source:
        eg. 'https://musify.club/release/linkin-park-hybrid-theory-2000-188'

        /html/musify/album_overview.html
        [] tracklist
        [] attributes
        [] ratings

        :param source:
        :param flat:
        :return:
        """
        album = Album(title="Hi :)")

        url = cls.parse_url(source.url)

        endpoint = cls.HOST + "/release/" + url.name_with_id
        r = cls.get_request(endpoint)
        if r is None:
            return album

        soup = BeautifulSoup(r.content, "html.parser")

        # <div class="card"><div class="card-body">...</div></div>
        cards_soup: BeautifulSoup = soup.find("div", {"class": "card-body"})
        if cards_soup is not None:
            card_soup: BeautifulSoup
            for card_soup in cards_soup.find_all("div", {"class": "playlist__item"}):
                album.song_collection.append(cls.parse_song_card(card_soup))
        album.update_tracksort()

        return album
