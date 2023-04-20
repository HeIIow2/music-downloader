from typing import Dict, List

import requests


class RotatingObject:
    """
    This will be used for RotatingProxies and invidious instances.
    """
    def __init__(self, object_list: list):
        self._object_list: list = object_list

        if len(self._object_list) <= 0:
            raise ValueError("There needs to be at least one item in a Rotating structure.")

        self._current_index = 0

    @property
    def object(self):
        return self._object_list[self._current_index]

    def __len__(self):
        return len(self._object_list)

    @property
    def next(self):
        self._current_index = (self._current_index + 1) % len(self._object_list)

        return self._object_list[self._current_index]


class RotatingProxy(RotatingObject):
    def __init__(self, proxy_list: List[Dict[str, str]], session_list: List[requests.Session] = None):
        self._session_list: List[requests.Session] = session_list
        if self._session_list is None:
            self._session_list = []

        super().__init__(proxy_list if len(proxy_list) > 0 else [{}])

    def register_session(self, session: requests.Session):
        self._session_list.append(session)
        session.proxies = self.current_proxy

    def rotate(self):
        new_proxy = self.next

        for session in self._session_list:
            session.proxies = new_proxy

    @property
    def current_proxy(self) -> Dict[str, str]:
        return super().object

    @property
    def next(self) -> Dict[str, str]:
        return super().object
