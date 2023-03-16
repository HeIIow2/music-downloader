from typing import List, Optional, Union
import requests
from bs4 import BeautifulSoup
import pycountry
import time

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
    string_processing,
    shared
)
from ..utils.shared import (
    MUSIFY_LOGGER as LOGGER
)


class Musify(Page):
    API_SESSION: requests.Session = requests.Session()
    API_SESSION.headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Connection": "keep-alive",
        "Referer": "https://musify.club/"
    }
    API_SESSION.proxies = shared.proxies

    SOURCE_TYPE = SourcePages.MUSIFY
    
    HOST = "https://musify.club"

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
    def get_soup_of_search(cls, query: str, trie=0) -> Optional[BeautifulSoup]:
        url = f"https://musify.club/search?searchText={query}"
        LOGGER.debug(f"Trying to get soup from {url}")
        try:
            r = cls.API_SESSION.get(url, timeout=15)
        except requests.exceptions.Timeout:
            return None
        if r.status_code != 200:
            if r.status_code in [503] and trie < cls.TRIES:
                LOGGER.warning(f"{cls.__name__} blocked downloading. ({trie}-{cls.TRIES})")
                LOGGER.warning(f"retrying in {cls.TIMEOUT} seconds again")
                time.sleep(cls.TIMEOUT)
                return cls.get_soup_of_search(query, trie=trie + 1)

            LOGGER.warning("too many tries, returning")
            return None
        return BeautifulSoup(r.content, features="html.parser")
    
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
        parsing following html:
        
        ```html
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
        ```
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
        #print(contact_container_soup.prettify)
        contacts = []
        
        # print(contact_container_soup)
        
        contact: BeautifulSoup
        for contact in contact_container_soup.find_all("div", {"class": "contacts__item"}):
            
            anchor_soup = contact.find("a")

            if anchor_soup is not None:
                url = anchor_soup.get("href")
            
                if url is not None:
                    #print(url)
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
        
        search_soup = cls.get_soup_of_search(query=query)
        if search_soup is None:
            return None
        
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
