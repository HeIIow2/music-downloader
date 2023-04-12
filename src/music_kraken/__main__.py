import music_kraken


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="A simple cli to easily test music_kraken. The full cli is in the making."
    )

    # arguments for debug purposes
    parser.add_argument(
        '-v', '--verbose',
        action="store_true",
        help="Sets the logging level to debug."
    )

    parser.add_argument(
        '-t', '--test',
        action="store_true",
        help="For the sake of testing. Equals: '-v -g test'"
    )

    # general arguments
    parser.add_argument(
        '-g', '--genre',
        help="Specifies the genre. (Will be overwritten by -t)"
    )

    parser.add_argument(
        '-a', '--all',
        action="store_true",
        help="If set it will download EVERYTHING the music downloader can find.\n"
             "For example weird compilations from musify."
    )

    arguments = parser.parse_args()

    if arguments.verbose or arguments.test:
        import logging
        print("Setting logging-level to DEBUG")
        logging.getLogger().setLevel(logging.DEBUG)

    # getting the genre
    genre: str = arguments.genre
    if arguments.test:
        genre = "test"

    music_kraken.cli(genre=genre, download_all=arguments.all)
