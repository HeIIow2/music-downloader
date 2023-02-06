# Diff Details

Date : 2023-02-06 10:33:12

Directory /home/lars/Projects/music-downloader/src

Total : 55 files,  171 codes, 111 comments, 54 blanks, all 336 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [src/create_custom_objects.py](/src/create_custom_objects.py) | Python | 80 | 3 | 18 | 101 |
| [src/goof.py](/src/goof.py) | Python | -116 | -6 | -29 | -151 |
| [src/metal_archives.py](/src/metal_archives.py) | Python | 45 | 6 | 17 | 68 |
| [src/music_kraken/__init__.py](/src/music_kraken/__init__.py) | Python | -55 | -6 | -15 | -76 |
| [src/music_kraken/audio_source/__init__.py](/src/music_kraken/audio_source/__init__.py) | Python | -10 | 0 | -5 | -15 |
| [src/music_kraken/audio_source/fetch_audio.py](/src/music_kraken/audio_source/fetch_audio.py) | Python | -75 | -12 | -20 | -107 |
| [src/music_kraken/audio_source/fetch_source.py](/src/music_kraken/audio_source/fetch_source.py) | Python | -54 | -1 | -16 | -71 |
| [src/music_kraken/audio_source/sources/__init__.py](/src/music_kraken/audio_source/sources/__init__.py) | Python | 0 | 0 | -1 | -1 |
| [src/music_kraken/audio_source/sources/local_files.py](/src/music_kraken/audio_source/sources/local_files.py) | Python | -40 | 0 | -18 | -58 |
| [src/music_kraken/audio_source/sources/musify.py](/src/music_kraken/audio_source/sources/musify.py) | Python | -136 | -9 | -37 | -182 |
| [src/music_kraken/audio_source/sources/source.py](/src/music_kraken/audio_source/sources/source.py) | Python | -11 | -5 | -8 | -24 |
| [src/music_kraken/audio_source/sources/youtube.py](/src/music_kraken/audio_source/sources/youtube.py) | Python | -71 | -4 | -24 | -99 |
| [src/music_kraken/database/__init__.py](/src/music_kraken/database/__init__.py) | Python | 6 | -1 | 1 | 6 |
| [src/music_kraken/database/database.py](/src/music_kraken/database/database.py) | Python | 238 | 10 | 66 | 314 |
| [src/music_kraken/database/get_song.py](/src/music_kraken/database/get_song.py) | Python | -40 | -5 | -11 | -56 |
| [src/music_kraken/database/new_database.py](/src/music_kraken/database/new_database.py) | Python | -402 | -110 | -107 | -619 |
| [src/music_kraken/database/objects/__init__.py](/src/music_kraken/database/objects/__init__.py) | Python | 5 | 0 | 2 | 7 |
| [src/music_kraken/database/objects/formatted_text.py](/src/music_kraken/database/objects/formatted_text.py) | Python | 48 | 57 | 16 | 121 |
| [src/music_kraken/database/objects/metadata.py](/src/music_kraken/database/objects/metadata.py) | Python | 6 | 16 | 11 | 33 |
| [src/music_kraken/database/objects/parents.py](/src/music_kraken/database/objects/parents.py) | Python | -6 | 0 | -4 | -10 |
| [src/music_kraken/database/objects/song.py](/src/music_kraken/database/objects/song.py) | Python | 65 | 12 | 9 | 86 |
| [src/music_kraken/database/objects/source.py](/src/music_kraken/database/objects/source.py) | Python | 70 | 31 | 28 | 129 |
| [src/music_kraken/database/song.py](/src/music_kraken/database/song.py) | Python | -125 | -20 | -45 | -190 |
| [src/music_kraken/lyrics/__init__.py](/src/music_kraken/lyrics/__init__.py) | Python | 0 | 0 | -1 | -1 |
| [src/music_kraken/lyrics/genius.py](/src/music_kraken/lyrics/genius.py) | Python | -115 | -16 | -42 | -173 |
| [src/music_kraken/lyrics/lyrics.py](/src/music_kraken/lyrics/lyrics.py) | Python | -36 | -25 | -20 | -81 |
| [src/music_kraken/metadata/__init__.py](/src/music_kraken/metadata/__init__.py) | Python | -6 | 0 | -2 | -8 |
| [src/music_kraken/metadata/metadata_fetch.py](/src/music_kraken/metadata/metadata_fetch.py) | Python | -257 | -24 | -65 | -346 |
| [src/music_kraken/metadata/metadata_search.py](/src/music_kraken/metadata/metadata_search.py) | Python | -253 | -40 | -72 | -365 |
| [src/music_kraken/metadata/sources/__init__.py](/src/music_kraken/metadata/sources/__init__.py) | Python | -3 | 0 | -2 | -5 |
| [src/music_kraken/metadata/sources/musicbrainz.py](/src/music_kraken/metadata/sources/musicbrainz.py) | Python | -42 | -6 | -9 | -57 |
| [src/music_kraken/not_used_anymore/__init__.py](/src/music_kraken/not_used_anymore/__init__.py) | Python | 0 | 0 | 3 | 3 |
| [src/music_kraken/not_used_anymore/fetch_audio.py](/src/music_kraken/not_used_anymore/fetch_audio.py) | Python | 75 | 12 | 20 | 107 |
| [src/music_kraken/not_used_anymore/fetch_source.py](/src/music_kraken/not_used_anymore/fetch_source.py) | Python | 54 | 1 | 16 | 71 |
| [src/music_kraken/not_used_anymore/metadata/__init__.py](/src/music_kraken/not_used_anymore/metadata/__init__.py) | Python | 6 | 0 | 2 | 8 |
| [src/music_kraken/not_used_anymore/metadata/metadata_fetch.py](/src/music_kraken/not_used_anymore/metadata/metadata_fetch.py) | Python | 257 | 24 | 65 | 346 |
| [src/music_kraken/not_used_anymore/metadata/metadata_search.py](/src/music_kraken/not_used_anymore/metadata/metadata_search.py) | Python | 253 | 40 | 72 | 365 |
| [src/music_kraken/not_used_anymore/metadata/sources/__init__.py](/src/music_kraken/not_used_anymore/metadata/sources/__init__.py) | Python | 3 | 0 | 2 | 5 |
| [src/music_kraken/not_used_anymore/metadata/sources/musicbrainz.py](/src/music_kraken/not_used_anymore/metadata/sources/musicbrainz.py) | Python | 42 | 6 | 12 | 60 |
| [src/music_kraken/not_used_anymore/sources/__init__.py](/src/music_kraken/not_used_anymore/sources/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/music_kraken/not_used_anymore/sources/genius.py](/src/music_kraken/not_used_anymore/sources/genius.py) | Python | 115 | 16 | 42 | 173 |
| [src/music_kraken/not_used_anymore/sources/local_files.py](/src/music_kraken/not_used_anymore/sources/local_files.py) | Python | 40 | 0 | 18 | 58 |
| [src/music_kraken/not_used_anymore/sources/musify.py](/src/music_kraken/not_used_anymore/sources/musify.py) | Python | 136 | 9 | 37 | 182 |
| [src/music_kraken/not_used_anymore/sources/source.py](/src/music_kraken/not_used_anymore/sources/source.py) | Python | 11 | 5 | 8 | 24 |
| [src/music_kraken/not_used_anymore/sources/youtube.py](/src/music_kraken/not_used_anymore/sources/youtube.py) | Python | 71 | 4 | 24 | 99 |
| [src/music_kraken/pages/__init__.py](/src/music_kraken/pages/__init__.py) | Python | 7 | 0 | 5 | 12 |
| [src/music_kraken/pages/abstract.py](/src/music_kraken/pages/abstract.py) | Python | 70 | 68 | 27 | 165 |
| [src/music_kraken/pages/encyclopaedia_metallum.py](/src/music_kraken/pages/encyclopaedia_metallum.py) | Python | 299 | 60 | 76 | 435 |
| [src/music_kraken/pages/youtube.py](/src/music_kraken/pages/youtube.py) | Python | 25 | 16 | 6 | 47 |
| [src/music_kraken/static_files/new_db.sql](/src/music_kraken/static_files/new_db.sql) | SQLite | 1 | 0 | 0 | 1 |
| [src/music_kraken/tagging/song.py](/src/music_kraken/tagging/song.py) | Python | -3 | 0 | -1 | -4 |
| [src/music_kraken/utils/shared.py](/src/music_kraken/utils/shared.py) | Python | 1 | 0 | 1 | 2 |
| [src/music_kraken/utils/string_processing.py](/src/music_kraken/utils/string_processing.py) | Python | 2 | 5 | 2 | 9 |
| [src/music_kraken_cli.py](/src/music_kraken_cli.py) | Python | -3 | 0 | 0 | -3 |
| [src/test.db](/src/test.db) | Database | -1 | 0 | 1 | 0 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details