from typing import Set, Type, Dict, List
from pathlib import Path
import re

from ...utils.shared import MUSIC_DIR, NOT_A_GENRE_REGEX
from ...utils.regex import URL_PATTERN
from ...utils.string_processing import fit_to_file_system
from ...utils.support_classes import Query, DownloadResult
from ...download.results import Results, SearchResults, Option, PageResults
from ...download.page_attributes import Pages
from ...pages import Page
from ...objects import Song, Album, Artist, DatabaseObject


"""
This is the implementation of the Shell

# Behaviour

## Searching

```mkshell
> s: {querry or url}

# examples
> s: https://musify.club/release/some-random-release-183028492
> s: r: #a an Artist #r some random Release
```

Searches for an url, or an query

### Query Syntax

```
#a {artist} #r {release} #t {track}
```

You can escape stuff like `#` doing this: `\#`

## Downloading

To download something, you either need a direct link, or you need to have already searched for options

```mkshell
> d: {option ids or direct url}

# examples
> d: 0, 3, 4
> d: 1
> d: https://musify.club/release/some-random-release-183028492
```

## Misc

### Exit

```mkshell
> q
> quit
> exit
> abort
```

### Current Options

```mkshell
> .
```

### Previous Options

```
> ..
```

"""

EXIT_COMMANDS = {"q", "quit", "exit", "abort"}
ALPHABET = "abcdefghijklmnopqrstuvwxyz"
PAGE_NAME_FILL = "-"
MAX_PAGE_LEN = 21


def get_existing_genre() -> List[str]:
    """
    gets the name of all subdirectories of shared.MUSIC_DIR,
    but filters out all directories, where the name matches with any patern
    from shared.NOT_A_GENRE_REGEX.
    """
    existing_genres: List[str] = []

    # get all subdirectories of MUSIC_DIR, not the files in the dir.
    existing_subdirectories: List[Path] = [f for f in MUSIC_DIR.iterdir() if f.is_dir()]

    for subdirectory in existing_subdirectories:
        name: str = subdirectory.name

        if not any(re.match(regex_pattern, name) for regex_pattern in NOT_A_GENRE_REGEX):
            existing_genres.append(name)

    existing_genres.sort()

    return existing_genres

def get_genre():
    existing_genres = get_existing_genre()
    for i, genre_option in enumerate(existing_genres):
        print(f"{i + 1:0>2}: {genre_option}")

    while True:
        genre = input("Id or new genre: ")

        if genre.isdigit():
            genre_id = int(genre) - 1
            if genre_id >= len(existing_genres):
                print(f"No genre under the id {genre_id + 1}.")
                continue

            return existing_genres[genre_id]

        new_genre = fit_to_file_system(genre)

        agree_inputs = {"y", "yes", "ok"}
        verification = input(f"create new genre \"{new_genre}\"? (Y/N): ").lower()
        if verification in agree_inputs:
            return new_genre
        
        
def help_message():
    print()
    print("""
to search:
> s: {query or url}
> s: https://musify.club/release/some-random-release-183028492
> s: #a {artist} #r {release} #t {track}

to download:
> d: {option ids or direct url}
> d: 0, 3, 4
> d: 1
> d: https://musify.club/release/some-random-release-183028492

have fun :3
          """.strip())
    print()


class Shell:
    """
    TODO:
    
    - Implement search and download for direct urls
    """
    
    def __init__(
            self,
            exclude_pages: Set[Type[Page]] = None, 
            exclude_shady: bool = False,
            max_displayed_options: int = 10,
            option_digits: int = 3,
            genre: str = None
    ) -> None:
        self.pages: Pages = Pages(exclude_pages=exclude_pages, exclude_shady=exclude_shady)
        
        self.page_dict: Dict[str, Type[Page]] = dict()
        
        self.max_displayed_options = max_displayed_options
        self.option_digits: int = option_digits
        
        self.current_results: Results = SearchResults
        
        self.genre = genre or get_genre()
        
        print()
        print(f"Downloading to: \"{self.genre}\"")
        print()

    
    def print_current_options(self):
        self.page_dict = dict()

        print()

        page_count = 0
        for option in self.current_results.formated_generator(max_items_per_page=self.max_displayed_options):
            if isinstance(option, Option):
                print(f"{option.index:0{self.option_digits}} {option.music_object.option_string}")
            else:
                prefix = ALPHABET[page_count%len(ALPHABET)]
                print(f"({prefix}) ------------------------{option.__name__:{PAGE_NAME_FILL}<{MAX_PAGE_LEN}}------------")
                
                self.page_dict[prefix] = option
                self.page_dict[option.__name__] = option
                
                page_count += 1

        print()

    def set_current_options(self, current_options: Results):
        self.current_results = current_options
    
    def _process_parsed(self, key_text: Dict[str, str], query: str) -> Query:
        song = None if not "t" in key_text else Song(title=key_text["t"], dynamic=True)
        album = None if not "r" in key_text else Album(title=key_text["r"], dynamic=True)
        artist = None if not "a" in key_text else Artist(name=key_text["a"], dynamic=True)
        
        if song is not None:
            song.album_collection.append(album)
            song.main_artist_collection.append(artist)
            return Query(raw_query=query, music_object=song)
        
        if album is not None:
            album.artist_collection.append(artist)
            return Query(raw_query=query, music_object=album)
        
        if artist is not None:
            return Query(raw_query=query, music_object=artist)
        
        return Query(raw_query=query)
    
    def search(self, query: str):
        if re.match(URL_PATTERN, query) is not None:
            page, data_object = self.pages.fetch_url(query)
            self.set_current_options(PageResults(page, data_object.options))
            self.print_current_options()
            return
        
        special_characters = "#\\"
        query = query + " "
        
        key_text = {}
        
        skip_next = False
        escape_next = False
        new_text = ""
        latest_key: str = None
        for i in range(len(query) - 1):
            current_char = query[i]
            next_char = query[i+1]
            
            if skip_next:
                skip_next = False
                continue
            
            if escape_next:
                new_text += current_char
                escape_next = False
            
            # escaping
            if current_char == "\\":
                if next_char in special_characters:
                    escape_next = True
                    continue
                
            if current_char == "#":
                if latest_key is not None:
                    key_text[latest_key] = new_text
                    new_text = ""
                    
                latest_key = next_char
                skip_next = True
                continue
            
            new_text += current_char
        
        if latest_key is not None:
            key_text[latest_key] = new_text
            
            
        parsed_query: Query = self._process_parsed(key_text, query)
        
        self.set_current_options(self.pages.search(parsed_query))
        self.print_current_options()
    
    def goto(self, index: int):
        page: Type[Page]
        music_object: DatabaseObject
        
        try:
            page, music_object = self.current_results.get_music_object_by_index(index)
        except KeyError:
            print()
            print(f"The option {index} doesn't exist.")
            print()
            return
        
        self.pages.fetch_details(music_object)
        
        self.set_current_options(PageResults(page, music_object.options))
        
        self.print_current_options()
        
    
    def download(self, download_str: str, download_all: bool = False) -> bool:
        to_download: List[DatabaseObject] = []

        if re.match(URL_PATTERN, download_str) is not None:
            _, music_objects = self.pages.fetch_url(download_str)
            to_download.append(music_objects)
            
        else:
            index: str
            for index in download_str.split(", "):
                if not index.strip().isdigit():
                    print()
                    print(f"Every download thingie has to be an index, not {index}.")
                    print()
                    return False
            
            for index in download_str.split(", "):
                to_download.append(self.current_results.get_music_object_by_index(int(index))[1])
        
        print()
        print("Downloading:")
        for download_object in to_download:
            print(download_object.option_string)
        print()
        
        _result_map: Dict[DatabaseObject, DownloadResult] = dict()
        
        for database_object in to_download:
            r = self.pages.download(music_object=database_object, genre=self.genre, download_all=download_all)
            _result_map[database_object] = r
            
        for music_object, result in _result_map.items():
            print()
            print(music_object.option_string)
            print(result)
            
        return True
    
    def process_input(self, input_str: str) -> bool:
        input_str = input_str.strip()
        processed_input: str = input_str.lower()
        
        if processed_input in EXIT_COMMANDS:
            return True
        
        if processed_input == ".":
            self.print_current_options()
            return False
        
        if processed_input.startswith("s: "):
            self.search(input_str[3:])
            return False
        
        if processed_input.startswith("d: "):
            return self.download(input_str[3:])
        
        if processed_input.isdigit():
            self.goto(int(processed_input))
            return False
        
        if processed_input != "help":
            print("Invalid input.")
        help_message()
        return False
    
    def mainloop(self):
        while True:
            if self.process_input(input("> ")):
                return
            