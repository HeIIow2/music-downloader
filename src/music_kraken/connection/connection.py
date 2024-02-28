import logging
import threading
import time
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse, urlunsplit, ParseResult
import copy
import inspect

import requests
import responses
from tqdm import tqdm
import merge_args

from .cache import Cache
from .rotating import RotatingProxy
from ..objects import Target
from ..utils.config import main_settings
from ..utils.support_classes.download_result import DownloadResult


class Connection:
    def __init__(
            self,
            host: str,
            proxies: List[dict] = None,
            tries: int = (len(main_settings["proxies"]) + 1) * main_settings["tries_per_proxy"],
            timeout: int = 7,
            logger: logging.Logger = logging.getLogger("connection"),
            header_values: Dict[str, str] = None,
            accepted_response_codes: Set[int] = None,
            semantic_not_found: bool = True,
            sleep_after_404: float = 0.0,
            heartbeat_interval=0,
            module: str = "general",
            cache_expiring_duration: float = 10
    ):
        if proxies is None:
            proxies = main_settings["proxies"]
        if header_values is None:
            header_values = dict()

        self.cache: Cache = Cache(module=module, logger=logger)
        self.cache_expiring_duration = cache_expiring_duration

        self.HEADER_VALUES = header_values

        self.LOGGER = logger
        self.HOST = urlparse(host)
        self.TRIES = tries
        self.TIMEOUT = timeout
        self.rotating_proxy = RotatingProxy(proxy_list=proxies)

        self.ACCEPTED_RESPONSE_CODES = accepted_response_codes or {200}
        self.SEMANTIC_NOT_FOUND = semantic_not_found
        self.sleep_after_404 = sleep_after_404

        self.session = requests.Session()
        self.session.headers = self.get_header(**self.HEADER_VALUES)
        self.session.proxies = self.rotating_proxy.current_proxy

        self.heartbeat_thread = None
        self.heartbeat_interval = heartbeat_interval

        self.lock: bool = False

    def start_heartbeat(self):
        if self.heartbeat_interval <= 0:
            self.LOGGER.warning(f"Can't start a heartbeat with {self.heartbeat_interval}s in between.")

        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, args=(self.heartbeat_interval,), daemon=True)
        self.heartbeat_thread.start()

    def heartbeat_failed(self):
        self.LOGGER.warning(f"The hearth couldn't beat.")

    def heartbeat(self):
        # Your code to send heartbeat requests goes here
        raise NotImplementedError("please implement the heartbeat function.")

    def _heartbeat_loop(self, interval: float):
        def heartbeat_wrapper():
            self.LOGGER.debug(f"The hearth is beating.")
            self.heartbeat()

        while True:
            heartbeat_wrapper()
            time.sleep(interval)

    def base_url(self, url: ParseResult = None):
        if url is None:
            url = self.HOST

        return urlunsplit((url.scheme, url.netloc, "", "", ""))

    def get_header(self, **header_values) -> Dict[str, str]:
        return {
            "user-agent": main_settings["user_agent"],
            "User-Agent": main_settings["user_agent"],
            "Connection": "keep-alive",
            "Host": self.HOST.netloc,
            "Referer": self.base_url(),
            "Accept-Language": main_settings["language"],
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
        headers = self.get_header(**(headers or {}))
        if not refer_from_origin:
            headers["Referer"] = self.base_url(url=url)

        return headers

    def save(self, r: requests.Response, name: str, error: bool = False, **kwargs):
        n_kwargs = {}
        if error:
            n_kwargs["module"] = "failed_requests"

        self.cache.set(r.content, name, expires_in=kwargs.get("expires_in", self.cache_expiring_duration), **n_kwargs)

    def request(
            self,
            url: str,
            timeout: float = None,
            headers: Optional[dict] = None,
            try_count: int = 0,
            accepted_response_codes: set = None,
            refer_from_origin: bool = True,
            raw_url: bool = False,
            sleep_after_404: float = None,
            is_heartbeat: bool = False,
            disable_cache: bool = None,
            method: str = None,
            name: str = "",
            **kwargs
    ) -> Optional[requests.Response]:
        if method is None:
            raise AttributeError("method is not set.")
        method = method.upper()
        disable_cache = headers.get("Cache-Control", "").lower() == "no-cache" if disable_cache is None else disable_cache
        accepted_response_codes = self.ACCEPTED_RESPONSE_CODES if accepted_response_codes is None else accepted_response_codes
        
        current_kwargs = copy.copy(locals())

        parsed_url = urlparse(url)
        headers = self._update_headers(
            headers=headers,
            refer_from_origin=refer_from_origin,
            url=parsed_url
        )

        if name != "" and not disable_cache:
            cached = self.cache.get(name)

            if cached is not None:
                with responses.RequestsMock() as resp:
                    resp.add(
                        method=method,
                        url=url,
                        body=cached,
                    )
                    return requests.request(method=method, url=url, timeout=timeout, headers=headers, **kwargs)

        if sleep_after_404 is None:
            sleep_after_404 = self.sleep_after_404
        if try_count >= self.TRIES:
            return

        if timeout is None:
            timeout = self.TIMEOUT

        request_url = parsed_url.geturl() if not raw_url else url

        r = None
        connection_failed = False
        try:
            if self.lock:
                self.LOGGER.info(f"Waiting for the heartbeat to finish.")
                while self.lock and not is_heartbeat:
                    pass
            
            self.lock = True
            r: requests.Response = requests.request(method=method, url=url, timeout=timeout, headers=headers, **kwargs)

            if r.status_code in accepted_response_codes:
                if not disable_cache:
                    self.save(r, name, **kwargs)
                return r

            if self.SEMANTIC_NOT_FOUND and r.status_code == 404:
                self.LOGGER.warning(f"Couldn't find url (404): {request_url}")
                return None

        # the server rejected the request, or the internet is lacking
        except requests.exceptions.Timeout:
            self.LOGGER.warning(f"Request timed out at \"{request_url}\": ({try_count}-{self.TRIES})")
            connection_failed = True
        except requests.exceptions.ConnectionError:
            self.LOGGER.warning(f"Couldn't connect to \"{request_url}\": ({try_count}-{self.TRIES})")
            connection_failed = True

        # this is important for thread safety
        finally:
            self.lock = False

        if not connection_failed:
            self.LOGGER.warning(f"{self.HOST.netloc} responded wit {r.status_code} "
                                f"at {url}. ({try_count}-{self.TRIES})")
            if r is not None:
                self.LOGGER.debug("request headers:\n\t"+ "\n\t".join(f"{k}\t=\t{v}" for k, v in r.request.headers.items()))
                self.LOGGER.debug("response headers:\n\t"+ "\n\t".join(f"{k}\t=\t{v}" for k, v in r.headers.items()))
                self.LOGGER.debug(r.content)
                
                if name != "":
                    self.save(r, name, error=True, **kwargs)

            if sleep_after_404 != 0:
                self.LOGGER.warning(f"Waiting for {sleep_after_404} seconds.")
                time.sleep(sleep_after_404)

        self.rotate()

        current_kwargs["try_count"] = current_kwargs.get("try_count", 0) + 1
        return self.request(**current_kwargs)

    @merge_args(request)
    def get(self, *args,  **kwargs) -> Optional[requests.Response]:
        return self.request(
            *args,
            method="GET",
            **kwargs
        )

    @merge_args(request)
    def post(
            self,
            *args,
            json: dict = None,
            **kwargs
    ) -> Optional[requests.Response]:
        r = self.request(
            *args,
            method="POST",
            json=json,
            **kwargs
        )
        if r is None:
            self.LOGGER.warning(f"payload: {json}")
        return r

    @merge_args(request)
    def stream_into(
            self,
            url: str,
            target: Target,
            name: str = "download",
            chunk_size: int = main_settings["chunk_size"],
            progress: int = 0,
            method: str = "GET",
            **kwargs
    ) -> DownloadResult:
        stream_kwargs = copy.copy(locals())

        if progress > 0:
            headers = dict() if headers is None else headers
            headers["Range"] = f"bytes={target.size}-"

        r = self.request(
            url=url,
            name=name,
            chunk_size=chunk_size,
            method=method,
            **kwargs
        )

        if r is None:
            return DownloadResult(error_message=f"Could not establish a stream from: {url}")

        target.create_path()
        total_size = int(r.headers.get('content-length'))
        progress = 0

        retry = False

        with target.open("ab") as f:
            """
            https://en.wikipedia.org/wiki/Kilobyte
            > The internationally recommended unit symbol for the kilobyte is kB.
            """

            with tqdm(total=total_size - target.size, unit='B', unit_scale=True, unit_divisor=1024, desc=name) as t:
                try:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        size = f.write(chunk)
                        progress += size
                        t.update(size)

                except requests.exceptions.ConnectionError:
                    if try_count >= self.TRIES:
                        self.LOGGER.warning(f"Stream timed out at \"{url}\": to many retries, aborting.")
                        return DownloadResult(error_message=f"Stream timed out from {url}, reducing the chunk_size might help.")

                    self.LOGGER.warning(f"Stream timed out at \"{url}\": ({try_count}-{self.TRIES})")
                    retry = True

            if total_size > progress:
                retry = True

            if retry:
                self.LOGGER.warning(f"Retrying stream...")
                accepted_response_codes.add(206)
                return self.stream_into(**stream_kwargs)

            return DownloadResult()
