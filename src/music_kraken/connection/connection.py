from typing import List, Dict, Callable, Optional, Set
from urllib.parse import urlparse, urlunsplit, ParseResult
import logging

import requests

from .rotating import RotatingProxy
from ..utils.shared import PROXIES_LIST


class Connection:
    def __init__(
            self,
            host: str,
            proxies: List[dict] = None,
            tries: int = (len(PROXIES_LIST) + 1) * 2,
            timeout: int = 7,
            logger: logging.Logger = logging.getLogger("connection"),
            header_values: Dict[str, str] = None,
            accepted_response_codes: Set[int] = None,
            semantic_not_found: bool = True
    ):
        if proxies is None:
            proxies = PROXIES_LIST
        if header_values is None:
            header_values = dict()

        self.HEADER_VALUES = header_values

        self.LOGGER = logger
        self.HOST = urlparse(host)
        self.TRIES = tries
        self.TIMEOUT = timeout
        self.rotating_proxy = RotatingProxy(proxy_list=proxies)

        self.ACCEPTED_RESPONSE_CODES = accepted_response_codes or {200}
        self.SEMANTIC_NOT_FOUND = semantic_not_found

        self._session_map: Dict[str] = {
            self.HOST.netloc: self.new_session()
        }

    def base_url(self, url: ParseResult = None):
        if url is None:
            url = self.HOST

        return urlunsplit((url.scheme, url.netloc, "", "", ""))

    def _register_session(self, session: requests.Session, **header_values):
        session.headers = self.get_header(**header_values)
        self.rotating_proxy.register_session(session)

    def new_session(
            self,
            url: ParseResult = None,
            refer_from_origin: bool = True
    ) -> requests.Session:

        header_values = self.HEADER_VALUES.copy()
        if url is not None:
            header_values["Host"] = url.netloc

            if not refer_from_origin:
                header_values["Referer"] = self.base_url(url=url)

        session = requests.Session()
        self._register_session(session=session, **header_values)

        return session

    def get_header(self, **header_values) -> Dict[str, str]:
        return {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
            "Connection": "keep-alive",
            "Host": self.HOST.netloc,
            "Referer": self.base_url(),
            **header_values
        }

    def rotate(self):
        self.rotating_proxy.rotate()

    def get_session_from_url(self, url: str, refer_from_origin: bool = True) -> requests.Session:
        parsed_url = urlparse(url)

        if parsed_url.netloc in self._session_map:
            print("saved session")
            return self._session_map[parsed_url.netloc]

        self._session_map[parsed_url.netloc] = self.new_session(
            url=parsed_url,
            refer_from_origin=refer_from_origin
        )
        return self._session_map[parsed_url.netloc]

    def _request(
            self,
            request: Callable,
            try_count: int,
            accepted_response_code: set,
            url: str,
            timeout: float,
            **kwargs
    ) -> Optional[requests.Response]:
        if try_count >= self.TRIES:
            return

        if timeout is None:
            timeout = self.TIMEOUT

        retry = False
        try:
            r = request(url=url, timeout=timeout, **kwargs)
        except requests.exceptions.Timeout:
            self.LOGGER.warning(f"Request timed out at \"{url}\": ({try_count}-{self.TRIES})")
            retry = True
        except requests.exceptions.ConnectionError:
            self.LOGGER.warning(f"Couldn't connect to \"{url}\": ({try_count}-{self.TRIES})")
            retry = True

        if not retry:
            if self.SEMANTIC_NOT_FOUND and r.status_code == 404:
                self.LOGGER.warning(f"Couldn't find url (404): {url}")
                return
            if r.status_code in accepted_response_code:
                return r

        print(r.content)
        print(r.headers)

        if not retry:
            self.LOGGER.warning(f"{self.HOST.netloc} responded wit {r.status_code} "
                                f"at {url}. ({try_count}-{self.TRIES})")
            self.LOGGER.debug(r.content)

        self.rotate()

        return self._request(
            request=request,
            try_count=try_count,
            accepted_response_code=accepted_response_code,
            url=url,
            timeout=timeout,
            **kwargs
        )

    def get(
            self,
            url: str,
            refer_from_origin: bool = True,
            stream: bool = False,
            accepted_response_codes: set = None,
            timeout: float = None,
            **kwargs
    ) -> Optional[requests.Response]:
        s = self.get_session_from_url(url, refer_from_origin)
        r = self._request(
            request=s.get,
            try_count=0,
            accepted_response_code=accepted_response_codes or self.ACCEPTED_RESPONSE_CODES,
            url=url,
            stream=stream,
            timeout=timeout,
            **kwargs
        )
        if r is None:
            self.LOGGER.warning(f"Max attempts ({self.TRIES}) exceeded for: GET:{url}")
        return r

    def post(
            self,
            url: str,
            json: dict,
            refer_from_origin: bool = True,
            stream: bool = False,
            accepted_response_codes: set = None,
            timeout: float = None,
            **kwargs
    ) -> Optional[requests.Response]:
        r = self._request(
            request=self.get_session_from_url(url, refer_from_origin).post,
            try_count=0,
            accepted_response_code=accepted_response_codes or self.ACCEPTED_RESPONSE_CODES,
            url=url,
            timeout=timeout,
            json=json,
            stream=stream,
            **kwargs
        )
        if r is None:
            self.LOGGER.warning(f"Max attempts ({self.TRIES}) exceeded for: GET:{url}")
            self.LOGGER.warning(f"payload: {json}")
        return r
