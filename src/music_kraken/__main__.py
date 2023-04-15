if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="A simple yet powerful cli to download music with music-kraken.",
        epilog="This is a cli for the developers, and it is shipped with music-krakens core.\n"
               "While it is a nice and solid cli it will lack some features.\n"
               "The proper cli and other frontends will be made or already have been made.\n"
               "To see all current frontends check the docs at: https://github.com/HeIIow2/music-downloader"
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
        '-a', '--all',
        action="store_true",
        help="If set it will download EVERYTHING the music downloader can find.\n"
             "For example weird compilations from musify."
    )

    parser.add_argument(
        '-g', '--genre',
        help="Specifies the genre. (Will be overwritten by -t)"
    )

    parser.add_argument(
        '-u', '--url',
        help="Downloads the content of given url."
    )

    parser.add_argument(
        '--settings',
        help="Opens a menu to modify the settings",
        action="store_true"
    )

    arguments = parser.parse_args()

    if arguments.verbose or arguments.test:
        import logging
        print("Setting logging-level to DEBUG")
        logging.getLogger().setLevel(logging.DEBUG)

    import music_kraken

    music_kraken.read()

    if arguments.settings:
        music_kraken.settings()
        exit()

    # getting the genre
    genre: str = arguments.genre
    if arguments.test:
        genre = "test"

    try:
        music_kraken.cli(
            genre=genre,
            download_all=arguments.all,
            direct_download_url=arguments.url
        )
    except KeyboardInterrupt:
        print("\n\nRaise an issue if I fucked up:\nhttps://github.com/HeIIow2/music-downloader/issues")
        music_kraken.exit_message()
