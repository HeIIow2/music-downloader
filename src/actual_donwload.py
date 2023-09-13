import music_kraken


if __name__ == "__main__":
    normally_download = [
        "s: #a Favorite #r Anarcho",
        "1",
        "d: 1, 5"
    ]

    direct_download = [
        "d: https://musify.club/release/crystal-f-x-2012-795181"
    ]
    
    fetch_musify_song = [
        "s: https://musify.club/track/blokkmonsta-schwartz-crystal-f-purer-hass-8369115"
    ]

    fetch_youtube_playlist = [
        "s: https://yt.artemislena.eu/playlist?list=OLAK5uy_kcUBiDv5ATbl-R20OjNaZ5G28XFanQOmM"
    ]

    download_youtube_playlist = ["d: https://www.youtube.com/playlist?list=OLAK5uy_lqI_c6aDF9q4DWJ4TBzt1AFQYx_FXfU4E"]
    
    youtube_search = [
        "s: #a Zombiez",
        "10",
        "d: 5"
    ]

    youtube_music_test = [
        "s: #a Only Smile #r Your best friend",
        "8",
        "2",
        "d: 2"
    ]

    cross_download = [
        "s: #a Psychonaut 4",
        "2",
        "d: 0"
    ]

    bandcamp_test = [
        "s: #a Ghost Bath",
        "3",
        "d: 0"
    ]

    
    music_kraken.cli.download(genre="test", command_list=bandcamp_test, process_metadata_anyway=True)