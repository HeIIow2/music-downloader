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
    SourcePages
)


class EncyclopaediaMetallum(Page):
    API_SESSION: requests.Session = requests.Session()
    API_SESSION.headers = {
        "Host": "www.metal-archives.com",
        "Connection": "keep-alive"
    }


    @classmethod
    def search_by_query(cls, query: str) -> List[MusicObject]:
        query_obj = cls.Query(query)

        if query_obj.is_raw:
            return cls.simple_search(query_obj)
        print(query_obj)

    @classmethod
    def simple_search(cls, query: Page.Query):
        """
        Searches the default endpoint from metal archives, which intern searches only
        for bands, but it is the default, thus I am rolling with it
        """
        endpoint = "https://www.metal-archives.com/search/ajax-band-search/?field=name&query={query}&sEcho=1&iColumns=3&sColumns=&iDisplayStart=0&iDisplayLength=200&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2"

        r = cls.API_SESSION.get(endpoint.format(query=query))
        if r.status_code != 200:
            LOGGER.warning(f"code {r.status_code} at {endpoint.format(query=query.query)}")
            return []

        print(r.json())
        return cls.get_many_artists_from_json(r.json()['aaData'])

    @classmethod
    def get_artist_from_json(cls, html, genre, country) -> Artist:
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
    def get_many_artists_from_json(cls, raw_artist_list: list) -> List[Artist]:
        return [cls.get_artist_from_json(raw_artist) for raw_artist in raw_artist_list]
