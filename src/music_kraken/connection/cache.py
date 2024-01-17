import json
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from functools import lru_cache
import logging

from ..utils.config import main_settings


@dataclass
class CacheAttribute:
    module: str
    name: str

    created: datetime
    expires: datetime

    @property
    def id(self):
        return f"{self.module}_{self.name}"

    @property
    def is_valid(self):
        return datetime.now() < self.expires

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Cache:
    def __init__(self, module: str, logger: logging.Logger):
        self.module = module
        self.logger: logging.Logger = logger

        self._dir = main_settings["cache_directory"]
        self.index = Path(self._dir, "index.json")

        if not self.index.is_file():
            with self.index.open("w") as i:
                i.write(json.dumps([]))

        self.cached_attributes: List[CacheAttribute] = []
        self._id_to_attribute = {}

        self._time_fields = {"created", "expires"}
        with self.index.open("r") as i:
            for c in json.loads(i.read()):
                for key in self._time_fields:
                    c[key] = datetime.fromisoformat(c[key])

                ca = CacheAttribute(**c)
                self.cached_attributes.append(ca)
                self._id_to_attribute[ca.id] = ca

    @lru_cache()
    def _init_module(self, module: str) -> Path:
        """
        :param module:
        :return: the module path
        """
        r = Path(self._dir, module)
        r.mkdir(exist_ok=True)
        return r

    def _write_attribute(self, cached_attribute: CacheAttribute, write: bool = True) -> bool:
        existing_attribute: Optional[CacheAttribute] = self._id_to_attribute.get(cached_attribute.id)
        if existing_attribute is not None:
            # the attribute exists
            if existing_attribute == cached_attribute:
                return True

            if existing_attribute.is_valid:
                return False

            existing_attribute.__dict__ = cached_attribute.__dict__
        else:
            self.cached_attributes.append(cached_attribute)
            self._id_to_attribute[cached_attribute.id] = cached_attribute

        if write:
            _json = []
            for c in self.cached_attributes:
                d = c.__dict__
                for key in self._time_fields:
                    d[key] = d[key].isoformat()

                _json.append(d)

            with self.index.open("w") as f:
                f.write(json.dumps(_json, indent=4))

        return True

    def set(self, content: bytes, name: str, expires_in: float = 10):
        """
        :param content:
        :param module:
        :param name:
        :param expires_in: the unit is days
        :return:
        """
        if name == "":
            return

        module_path = self._init_module(self.module)

        cache_attribute = CacheAttribute(
            module=self.module,
            name=name,
            created=datetime.now(),
            expires=datetime.now() + timedelta(days=expires_in),
        )
        self._write_attribute(cache_attribute)

        cache_path = Path(module_path, name)
        with cache_path.open("wb") as content_file:
            self.logger.debug(f"writing cache to {cache_path}")
            content_file.write(content)

    def get(self, name: str) -> Optional[bytes]:
        path = Path(self._dir, self.module, name)

        if not path.is_file():
            return None

        # check if it is outdated
        existing_attribute: CacheAttribute = self._id_to_attribute[f"{self.module}_{name}"]
        if not existing_attribute.is_valid:
            return

        with path.open("rb") as f:
            return f.read()
