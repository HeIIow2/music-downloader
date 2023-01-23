from typing import List

from .abstract import Page
from ..database import MusicObject


class EncyclopaediaMetallum(Page):
    @classmethod
    def search_by_query(cls, query: str) -> List[MusicObject]:
        query_obj = cls.Query(query)

        if query_obj.is_raw:
            return cls.simple_search(query_obj)
        print(query_obj)

    @classmethod
    def simple_search(cls, query: Page.Query):
        pass
