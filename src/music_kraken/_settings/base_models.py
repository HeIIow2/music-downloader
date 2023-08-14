from typing import Optional, List, Union, Dict
from collections.abc import Iterable
from pathlib import Path

import toml


def comment_string(uncommented_string: str) -> str:
    _fragments = uncommented_string.split("\n")
    _fragments = ["# " + frag for frag in _fragments]
    return "\n".join(_fragments)


class Comment:
    def __init__(self, value: str) -> None:
        self.value: str = value

    @property
    def uncommented(self) -> str:
        return self.value

    @property
    def commented(self) -> str:
        return comment_string(self.value)

    def __str__(self) -> str:
        return self.commented


class Attribute:
    def __init__(self, data: dict, comment: Optional[str] = None) -> None:
        self.data: dict = data
        self.comment: Optional[Comment] = None if comment is None else Comment(
            comment)

    @property
    def toml_string(self) -> str:
        _data_string = toml.dumps(self.data)
        components: List[str] = [_data_string]

        if self.comment is not None:
            components.append(self.comment.commented)

        return "\n".join(components)

    def __setitem__(self, key: str, value):
        if key not in self.data:
            self.data[key] = value

        if isinstance(self.data[key], dict) and isinstance(value, dict):
            self.data[key].update(value)

        self.data[key] = value


class ConfigFile:
    def __init__(self, config_file: Path, data: List[Union[Attribute, Comment]]) -> None:
        self.config_file: Path = config_file

        self.unknown_attribute: Attribute = Attribute(
            {}, "This is the attribute is for all unknown attributes.")

        self._data: List[Union[Attribute, Comment]] = data
        self._key_attribute_map: Dict[str, Attribute] = {}
        for attribute in self._data:
            if isinstance(attribute, Comment):
                continue

            for key in attribute.data:
                self._key_attribute_map[key] = attribute

    def load(self):
        self.update(toml.load(self.config_file.open("r"), encoding="utf-8"))

    def dump(self):
        with self.config_file.open("w", encoding="utf-8") as config_file:
            config_file.write(self.toml_string)

    def update(self, data: dict):
        for key, value in data.items():
            if key not in self._key_attribute_map:
                self._key_attribute_map[key] = self.unknown_attribute
                self.unknown_attribute[key] = value
                continue

            self._key_attribute_map[key][key] = value

    @property
    def toml_string(self) -> str:
        components: List[str] = []
        for attribute in self._data:
            if isinstance(attribute, Attribute):
                components.append(attribute.toml_string)

        components.append(self.unknown_attribute.toml_string)

        return "\n\n".join(components)

    def __str__(self) -> str:
        return self.toml_string


if __name__ == "__main__":
    settings = ConfigFile(Path("/home/lars/.config/music-kraken/music-kraken.toml"), [
        Attribute({
            "happy_message": [
                "Support the artist.",
                "Star Me: https://github.com/HeIIow2/music-downloader",
                "🏳️‍⚧️🏳️‍⚧️ Trans rights are human rights. 🏳️‍⚧️🏳️‍⚧️",
                "🏳️‍⚧️🏳️‍⚧️ Trans women are women, trans men are men, and enbies are enbies. 🏳️‍⚧️🏳️‍⚧️",
                "🏴‍☠️🏴‍☠️ Unite under one flag, fck borders. 🏴‍☠️🏴‍☠️",
                "Join my Matrix Space: https://matrix.to/#/#music-kraken:matrix.org",
                "Gotta love the BPJM ;-;",
                "🏳️‍⚧️🏳️‍⚧️ Protect trans youth. 🏳️‍⚧️🏳️‍⚧️",
                "Nonstop Progressive Marxism.",
            ],
            "bitrate": 66.6
        },
            comment="this is a test section"
        ),
        Attribute({
            "# hihi": "byebey"
        })
    ])

    print(settings)
    settings.dump()
