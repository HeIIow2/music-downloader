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

    music_kraken.cli.download(genre="test", command_list=download_youtube_playlist, process_metadata_anyway=True)
