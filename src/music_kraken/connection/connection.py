import time
from typing import List, Dict, Callable, Optional, Set
from urllib.parse import urlparse, urlunsplit, ParseResult
import logging

import requests
from tqdm import tqdm

from .rotating import RotatingProxy
from ..utils.shared import PROXIES_LIST, CHUNK_SIZE
from ..utils.support_classes import DownloadResult
from ..objects import Target


class Connection:
    def __init__(
            self,
            host: str,
            proxies: List[dict] = None,
            tries: int = (len(PROXIES_LIST) + 1) * 4,
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

        self.session = requests.Session()
        self.session.headers = self.get_header(**self.HEADER_VALUES)
        self.session.proxies = self.rotating_proxy.current_proxy

    def base_url(self, url: ParseResult = None):
        if url is None:
            url = self.HOST

        return urlunsplit((url.scheme, url.netloc, "", "", ""))

    def get_header(self, **header_values) -> Dict[str, str]:
        return {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Connection": "keep-alive",
            # "Host": self.HOST.netloc,
            "Referer": self.base_url(),
            **header_values
        }

    def rotate(self):
        self.session.proxies = self.rotating_proxy.rotate()

    def _update_headers(
            self,
            headers: Optional[dict],
            refer_from_origin: bool,
            url: ParseResult
    ) -> Dict[str, str]:
        if headers is None:
            headers = dict()

        if not refer_from_origin:
            headers["Referer"] = self.base_url(url=url)

        return headers

    def _request(
            self,
            request: Callable,
            try_count: int,
            accepted_response_codes: set,
            url: str,
            timeout: float,
            headers: dict,
            refer_from_origin: bool = True,
            raw_url: bool = False,
            wait_on_403: bool = True,
            **kwargs
    ) -> Optional[requests.Response]:
        if try_count >= self.TRIES:
            return

        if timeout is None:
            timeout = self.TIMEOUT

        parsed_url = urlparse(url)

        headers = self._update_headers(
            headers=headers,
            refer_from_origin=refer_from_origin,
            url=parsed_url
        )

        request_url = parsed_url.geturl() if not raw_url else url

        connection_failed = False
        try:
            r: requests.Response = request(request_url, timeout=timeout, headers=headers, **kwargs)

            if r.status_code in accepted_response_codes:
                return r

            if self.SEMANTIC_NOT_FOUND and r.status_code == 404:
                self.LOGGER.warning(f"Couldn't find url (404): {request_url}")
                return None

        except requests.exceptions.Timeout:
            self.LOGGER.warning(f"Request timed out at \"{request_url}\": ({try_count}-{self.TRIES})")
            connection_failed = True
        except requests.exceptions.ConnectionError:
            self.LOGGER.warning(f"Couldn't connect to \"{request_url}\": ({try_count}-{self.TRIES})")
            connection_failed = True

        if not connection_failed:
            self.LOGGER.warning(f"{self.HOST.netloc} responded wit {r.status_code} "
                                f"at {url}. ({try_count}-{self.TRIES})")
            self.LOGGER.debug(r.content)
            if wait_on_403:
                self.LOGGER.warning(f"Waiting for 5 seconds.")
                time.sleep(5)

        self.rotate()

        return self._request(
            request=request,
            try_count=try_count+1,
            accepted_response_codes=accepted_response_codes,
            url=url,
            timeout=timeout,
            headers=headers,
            **kwargs
        )

    def get(
            self,
            url: str,
            refer_from_origin: bool = True,
            stream: bool = False,
            accepted_response_codes: set = None,
            timeout: float = None,
            headers: dict = None,
            raw_url: bool = False,
            **kwargs
    ) -> Optional[requests.Response]:
        if accepted_response_codes is None:
            accepted_response_codes = self.ACCEPTED_RESPONSE_CODES

        r = self._request(
            request=self.session.get,
            try_count=0,
            accepted_response_codes=accepted_response_codes,
            url=url,
            timeout=timeout,
            headers=headers,
            raw_url=raw_url,
            refer_from_origin=refer_from_origin,
            stream=stream,
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
            headers: dict = None,
            raw_url: bool = False,
            **kwargs
    ) -> Optional[requests.Response]:
        r = self._request(
            request=self.session.post,
            try_count=0,
            accepted_response_codes=accepted_response_codes or self.ACCEPTED_RESPONSE_CODES,
            url=url,
            timeout=timeout,
            headers=headers,
            refer_from_origin=refer_from_origin,
            raw_url=raw_url,
            json=json,
            stream=stream,
            **kwargs
        )
        if r is None:
            self.LOGGER.warning(f"Max attempts ({self.TRIES}) exceeded for: GET:{url}")
            self.LOGGER.warning(f"payload: {json}")
        return r

    def stream_into(
            self,
            url: str,
            target: Target,
            description: str = "download",
            refer_from_origin: bool = True,
            accepted_response_codes: set = None,
            timeout: float = None,
            headers: dict = None,
            raw_url: bool = False,
            chunk_size: int = CHUNK_SIZE,
            try_count: int = 0,
            progress: int = 0,
            **kwargs
    ) -> DownloadResult:

        if progress > 0:
            if headers is None:
                headers = dict()
            headers["Range"] = f"bytes={target.size}-"

        if accepted_response_codes is None:
            accepted_response_codes = self.ACCEPTED_RESPONSE_CODES
        
        r = self._request(
            request=self.session.get,
            try_count=0,
            accepted_response_codes=accepted_response_codes,
            url=url,
            timeout=timeout,
            headers=headers,
            raw_url=raw_url,
            refer_from_origin=refer_from_origin,
            stream=True,
            **kwargs
        )

        if r is None:
            return DownloadResult(error_message=f"Could not establish connection to: {url}")

        target.create_path()
        total_size = int(r.headers.get('content-length'))
        progress = 0

        retry = False

        with target.open("ab") as f:
            """
            https://en.wikipedia.org/wiki/Kilobyte
            > The internationally recommended unit symbol for the kilobyte is kB.
            """
                
            with tqdm(total=total_size-target.size, unit='B', unit_scale=True, unit_divisor=1024, desc=description) as t:
                try:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        size = f.write(chunk)
                        progress += size
                        t.update(size)

                except requests.exceptions.ConnectionError:
                    if try_count >= self.TRIES:
                        self.LOGGER.warning(f"Stream timed out at \"{url}\": to many retries, aborting.")
                        return DownloadResult(error_message=f"Stream timed out from {url}, reducing the chunksize might help.")

                    self.LOGGER.warning(f"Stream timed out at \"{url}\": ({try_count}-{self.TRIES})")
                    retry = True

            if total_size > progress:
                retry = True


            if retry:
                self.LOGGER.warning(f"Retrying stream...")
                accepted_response_codes.add(206)
                return self.stream_into(
                    url = url,
                    target = target,
                    description = description,
                    try_count=try_count+1,
                    progress=progress,
                    accepted_response_codes=accepted_response_codes,
                    timeout=timeout,
                    headers=headers,
                    raw_url=raw_url,
                    refer_from_origin=refer_from_origin,
                    chunk_size=chunk_size,
                    **kwargs
                )

            return DownloadResult()
