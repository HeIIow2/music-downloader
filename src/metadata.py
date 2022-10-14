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
            self.set_options([musicbrainzngs.search_artists(query), musicbrainzngs.search_release_groups(query), musicbrainzngs.search_releases(query)])
        elif artist is not None:
            self.set_options([musicbrainzngs.search_artists(artist=artist)])

    def browse_artist(self, artist):
        return

    def browse_option(self, option, index: int):
        if not option.choose(index):
            return False

        self.current_chosen_option = option.get_current_option()
        option_kind = self.current_chosen_option['kind']
        if option_kind == "artist":
            return self.browse_artist(self.current_chosen_option)

    def choose(self, index):
        if not self.current_options.choose(index):
            return self.current_options


    def get_options(self):
        return self.current_options

    def set_options(self, results):
        option_instance = self.Options(results=results)
        self.options_history.append(option_instance)
        self.current_options = option_instance

        return option_instance

    options = property(fget=get_options)

    class Options:
        def __init__(self, results: list):
            self.results = results

            self.headers = {
                "artist": "found {count} artists:\n"
            }

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
            if len(self.result_list) <= index -1:
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
            print(release)
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
                if "release-group-list" in option_set:
                    self.set_release_values(option_set)
                    continue
                if "release-list" in option_set:
                    self.set_track_values(option_set)
                    continue
                print(option_set)

        def set_artist_values(self, option_set: dict):
            self.artist_count += option_set['artist-count']
            for artist in option_set['artist-list']:
                artist['kind'] = "artist"
                self.result_list.append(artist)

        def set_release_values(self, option_set: dict):
            self.release_count += option_set['release-group-count']
            for release in option_set['release-group-list']:
                release['kind'] = "release"
                self.result_list.append(release)

        def set_track_values(self, option_set: dict):
            self.artist_count += option_set['release-count']
            for track in option_set['release-list']:
                track['kind'] = "track"
                self.result_list.append(track)




if __name__ == "__main__":
    search = Search(query="psychonaut 4")
    print(search.options)
    search.choose(0)
