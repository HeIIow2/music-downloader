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
        return f"{query.artist or '*'} - {query.album * '*'} - {query.song or '*'}"

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
                LOGGER.warning(f"youtube blocked downloading. ({trie}-{cls.TRIES})")
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
        print(contact)
        return Album(title="")
    
    @classmethod
    def parse_contact_container(cls, contact_container_soup: BeautifulSoup) -> List[Union[Artist, Album]]:
        # print(contact_container_soup.prettify)
        contacts = []
        
        # print(contact_container_soup)
        
        contact: BeautifulSoup
        for contact in contact_container_soup.find_all("div", {"class": "contacts__item"}):
            # print(contact)
            
            anchor_soup = contact.find("a")
            if anchor_soup is not None:
                url = anchor_soup.get("href")
                if url is not None:
                    print(url)
                    if "artist" in url:
                        contacts.append(cls.parse_artist_contact(contact))
                    elif "release" in url:
                        contacts.append(cls.parse_album_contact(contact))
                        break
        return contacts
    
    @classmethod
    def parse_playlist_soup(cls, playlist_soup: BeautifulSoup) -> List[Song]:
        # print(playlist_soup.prettify)
        return []

    @classmethod
    def plaintext_search(cls, query: str) -> List[MusicObject]:
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

        """
        # get the soup of the container with all track results
        tracklist_container_soup = search_soup.find_all("div", {"class": "playlist"})
        if len(tracklist_container_soup) == 0:
            return []
        if len(tracklist_container_soup) != 1:
            LOGGER.warning("HTML Layout of https://musify.club/ changed. (or bug)")
        tracklist_container_soup = tracklist_container_soup[0]

        tracklist_soup = tracklist_container_soup.find_all("div", {"class": "playlist__details"})

        def parse_track_soup(_track_soup):
            anchor_soups = _track_soup.find_all("a")
            artist_ = anchor_soups[0].text.strip()
            track_ = anchor_soups[1].text.strip()
            url_ = anchor_soups[1]['href']
            return artist_, track_, url_

        # check each track in the container, if they match
        for track_soup in tracklist_soup:
            artist_option, title_option, track_url = parse_track_soup(track_soup)

            title_match, title_distance = phonetic_compares.match_titles(title, title_option)
            artist_match, artist_distance = phonetic_compares.match_artists(artist, artist_option)

            logging.debug(f"{(title, title_option, title_match, title_distance)}")
            logging.debug(f"{(artist, artist_option, artist_match, artist_distance)}")

            if not title_match and not artist_match:
                return cls.get_download_link(track_url)
        """

        return search_results

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
