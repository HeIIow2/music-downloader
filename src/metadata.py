import musicbrainzngs

musicbrainzngs.set_useragent("metadata receiver", "0.1", "https://github.com/HeIIow2/music-downloader")

KNOWN_KIND_OF_OPTIONS = ["artist", "release", "track"]


class Search:
    def __init__(self, query: str = None, artist: str = None):
        if query is None and artist is None:
            raise ValueError("no query provided")

        self.options_history = []
        self.current_options = None
        self.current_chosen_option = None

        # initial search
        if query is not None:
            self.set_options(self.Options([musicbrainzngs.search_artists(query), musicbrainzngs.search_releases(query),
                                           musicbrainzngs.search_recordings(query)]))
        elif artist is not None:
            self.set_options(self.Options([musicbrainzngs.search_artists(artist=artist)]))

    def browse_artist(self, artist: dict, limit: int = 25):
        options_sets = [
            {"artist-list": [artist, ], "artist-count": 1},
            musicbrainzngs.browse_releases(artist=artist["id"], limit=limit),
            musicbrainzngs.browse_recordings(artist=artist["id"], limit=limit)
        ]
        return self.set_options(self.Options(options_sets))

    def browse_release(self, release: dict, limit: int = 25):
        options_sets = [
            musicbrainzngs.browse_artists(release=release["id"], limit=limit),
            {"release-list": [release, ], "release-count": 1},
            musicbrainzngs.browse_recordings(release=release["id"], limit=limit)
        ]
        return self.set_options(self.Options(options_sets))

    def browse_track(self, track: dict, limit: int = 25):
        options_sets = [
            musicbrainzngs.browse_artists(recording=track["id"], limit=limit),
            musicbrainzngs.browse_releases(recording=track["id"], limit=limit),
            {"recording-list": [track, ], "recording-count": 1}
        ]
        return self.set_options(self.Options(options_sets))

    def choose(self, index, limit: int = 25, ignore_limit_for_tracklist: bool = True):
        if not self.current_options.choose(index):
            return self.current_options

        self.current_chosen_option = self.current_options.get_current_option()
        kind = self.current_chosen_option['kind']
        if kind == 'artist':
            return self.browse_artist(self.current_chosen_option, limit=limit)
        if kind == 'release':
            release_limit = limit if not ignore_limit_for_tracklist else 100
            return self.browse_release(self.current_chosen_option, limit=release_limit)
        if kind == 'track':
            track_limit = limit if not ignore_limit_for_tracklist else 100
            return self.browse_track(self.current_chosen_option, limit=track_limit)

        return self.current_options

    def get_options(self):
        return self.current_options

    def set_options(self, option_instance):
        self.options_history.append(option_instance)
        self.current_options = option_instance

        return option_instance

    def get_previous_options(self):
        self.options_history.pop(-1)
        self.current_options = self.options_history[-1]
        return self.current_options

    options = property(fget=get_options)

    class Options:
        def __init__(self, results: list):
            self.results = results

            self.artist_count = 0
            self.release_count = 0
            self.track_count = 0
            self.result_list = []
            self.set_options_values()

            self.current_option_ind = None

        def get_current_option(self):
            if self.current_option_ind is None:
                raise Exception("It must first be chosen, which option to get, before getting it")

            return self.result_list[self.current_option_ind]

        def choose(self, index: int) -> bool:
            if len(self.result_list) <= index - 1:
                return False
            self.current_option_ind = index
            return True

        def get_string_for_artist(self, artist: dict) -> str:
            string = f"'{artist['name']}'"
            if "country" in artist:
                string += f" from {artist['country']}"
            if 'disambiguation' in artist:
                string += f", '{artist['disambiguation']}'"
            return string + "\n"

        def get_string_for_release(self, release: dict) -> str:
            string = ""
            if "type" in release:
                string += f"the {release['type']} titled "
            string += f"'{release['title']}'"
            if "artist-credit-phrase" in release:
                string += f" by: {release['artist-credit-phrase']}"

            return string + "\n"

        def get_string_for_tracks(self, tracks: dict) -> str:
            # I know it's not the best practice but whatever
            return self.get_string_for_release(tracks)

        def get_string_for_option(self, option: dict) -> str:
            kind = option['kind']
            if kind == "artist":
                return self.get_string_for_artist(option)
            if kind == "release":
                return self.get_string_for_release(option)
            if kind == "track":
                return self.get_string_for_tracks(option)
            return "Error\n"

        def __str__(self) -> str:
            string = f"artists: {self.artist_count}; releases {self.release_count}; tracks {self.track_count}\n"
            for i, option in enumerate(self.result_list):
                string += f"{i})\t{option['kind']}:\t" + self.get_string_for_option(option)
            return string

        def set_options_values(self):
            for option_set in self.results:
                if "artist-list" in option_set:
                    self.set_artist_values(option_set)
                    continue
                if "release-list" in option_set:
                    self.set_release_values(option_set)
                    continue
                if "recording-list" in option_set:
                    self.set_track_values(option_set)
                    continue

        def set_artist_values(self, option_set: dict):
            self.artist_count += option_set['artist-count']
            for artist in option_set['artist-list']:
                artist['kind'] = "artist"
                self.result_list.append(artist)

        def set_release_values(self, option_set: dict):
            self.release_count += option_set['release-count']
            for release in option_set['release-list']:
                release['kind'] = "release"
                self.result_list.append(release)

        def set_track_values(self, option_set: dict):
            self.track_count += option_set['recording-count']
            for track in option_set['recording-list']:
                track['kind'] = "track"
                self.result_list.append(track)


def automated_demo():
    search = Search(query="psychonaut 4")
    print(search.options)
    print(search.choose(0))
    print(search.choose(2))
    print(search.choose(4))
    print(search.get_previous_options())
    print(search.choose(6))


if __name__ == "__main__":
    automated_demo()
