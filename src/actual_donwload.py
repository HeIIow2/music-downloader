import music_kraken


if __name__ == "__main__":
    normally_download = [
        "s: #a Ghost Bath",
        "1",
        "d: 1, 5"
    ]

    direct_download = [
        "d: https://musify.club/release/crystal-f-x-2012-795181"
    ]
    
    youtube_search = [
        "s: #a Zombiez",
        "10",
        "8"
    ]

    music_kraken.cli(genre="test", command_list=direct_download)
