import json
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from .config import main_settings


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
    def __init__(self):
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

                self.cached_attributes.append(**c)

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
            cached_attribute = existing_attribute
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

    def set(self, content: bytes, module: str, name: str, expires_in: int = 10):
        """
        :param content:
        :param module:
        :param name:
        :param expires_in: the unit is days
        :return:
        """

        module_path = self._init_module(module)

        cache_attribute = CacheAttribute(
            module=module,
            name=name,
            created=datetime.now(),
            expires=datetime.now() + timedelta(days=expires_in),
        )
        self._write_attribute(cache_attribute)

        with Path(module_path, name).open("wb") as content_file:
            content_file.write(content)
