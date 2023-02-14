# Details

Date : 2023-01-17 16:43:06

Directory /home/lars/Projects/music-downloader/src

Total : 49 files,  3402 codes, 663 comments, 973 blanks, all 5038 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [src/__init__.py](/src/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/goof.py](/src/goof.py) | Python | 116 | 6 | 29 | 151 |
| [src/music_kraken/__init__.py](/src/music_kraken/__init__.py) | Python | 118 | 32 | 48 | 198 |
| [src/music_kraken/__main__.py](/src/music_kraken/__main__.py) | Python | 3 | 2 | 3 | 8 |
| [src/music_kraken/audio_source/__init__.py](/src/music_kraken/not_used_anymore/__init__.py) | Python | 10 | 0 | 5 | 15 |
| [src/music_kraken/audio_source/fetch_audio.py](/src/music_kraken/not_used_anymore/fetch_audio.py) | Python | 75 | 12 | 20 | 107 |
| [src/music_kraken/audio_source/fetch_source.py](/src/music_kraken/not_used_anymore/fetch_source.py) | Python | 54 | 1 | 16 | 71 |
| [src/music_kraken/audio_source/sources/__init__.py](/src/music_kraken/not_used_anymore/sources/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/music_kraken/audio_source/sources/local_files.py](/src/music_kraken/not_used_anymore/sources/local_files.py) | Python | 40 | 0 | 18 | 58 |
| [src/music_kraken/audio_source/sources/musify.py](/src/music_kraken/not_used_anymore/sources/musify.py) | Python | 136 | 9 | 37 | 182 |
| [src/music_kraken/audio_source/sources/source.py](/src/music_kraken/not_used_anymore/sources/source.py) | Python | 11 | 5 | 8 | 24 |
| [src/music_kraken/audio_source/sources/youtube.py](/src/music_kraken/not_used_anymore/sources/youtube.py) | Python | 71 | 4 | 24 | 99 |
| [src/music_kraken/database/__init__.py](/src/music_kraken/database/__init__.py) | Python | 12 | 1 | 4 | 17 |
| [src/music_kraken/database/database.py](/src/music_kraken/database/old_database.py) | Python | 191 | 102 | 45 | 338 |
| [src/music_kraken/database/get_song.py](/src/music_kraken/database/get_song.py) | Python | 40 | 5 | 11 | 56 |
| [src/music_kraken/database/new_database.py](/src/music_kraken/database/old_database.py) | Python | 401 | 109 | 107 | 617 |
| [src/music_kraken/database/objects/__init__.py](/src/music_kraken/objects/__init__.py) | Python | 14 | 0 | 4 | 18 |
| [src/music_kraken/database/objects/artist.py](/src/music_kraken/objects/artist.py) | Python | 18 | 0 | 5 | 23 |
| [src/music_kraken/database/objects/metadata.py](/src/music_kraken/objects/metadata.py) | Python | 245 | 52 | 50 | 347 |
| [src/music_kraken/database/objects/parents.py](/src/music_kraken/objects/parents.py) | Python | 46 | 8 | 23 | 77 |
| [src/music_kraken/database/objects/song.py](/src/music_kraken/objects/song.py) | Python | 258 | 52 | 76 | 386 |
| [src/music_kraken/database/objects/source.py](/src/music_kraken/objects/source.py) | Python | 46 | 7 | 13 | 66 |
| [src/music_kraken/database/song.py](/src/music_kraken/database/song.py) | Python | 125 | 20 | 45 | 190 |
| [src/music_kraken/database/temp_database.py](/src/music_kraken/database/temp_database.py) | Python | 12 | 0 | 8 | 20 |
| [src/music_kraken/lyrics/__init__.py](/src/music_kraken/lyrics/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/music_kraken/lyrics/genius.py](/src/music_kraken/not_used_anymore/sources/genius.py) | Python | 115 | 16 | 42 | 173 |
| [src/music_kraken/lyrics/lyrics.py](/src/music_kraken/lyrics/lyrics.py) | Python | 36 | 25 | 20 | 81 |
| [src/music_kraken/metadata/__init__.py](/src/music_kraken/not_used_anymore/metadata/__init__.py) | Python | 6 | 0 | 2 | 8 |
| [src/music_kraken/metadata/metadata_fetch.py](/src/music_kraken/not_used_anymore/metadata/metadata_fetch.py) | Python | 257 | 24 | 65 | 346 |
| [src/music_kraken/metadata/metadata_search.py](/src/music_kraken/not_used_anymore/metadata/metadata_search.py) | Python | 253 | 40 | 72 | 365 |
| [src/music_kraken/metadata/sources/__init__.py](/src/music_kraken/not_used_anymore/metadata/sources/__init__.py) | Python | 3 | 0 | 2 | 5 |
| [src/music_kraken/metadata/sources/musicbrainz.py](/src/music_kraken/not_used_anymore/metadata/sources/musicbrainz.py) | Python | 42 | 6 | 9 | 57 |
| [src/music_kraken/static_files/new_db.sql](/src/music_kraken/static_files/new_db.sql) | SQLite | 71 | 0 | 10 | 81 |
| [src/music_kraken/static_files/temp_database_structure.sql](/src/music_kraken/static_files/temp_database_structure.sql) | SQLite | 135 | 0 | 10 | 145 |
| [src/music_kraken/tagging/__init__.py](/src/music_kraken/tagging/__init__.py) | Python | 8 | 0 | 2 | 10 |
| [src/music_kraken/tagging/id3.py](/src/music_kraken/tagging/id3.py) | Python | 51 | 4 | 20 | 75 |
| [src/music_kraken/tagging/song.py](/src/music_kraken/tagging/song.py) | Python | 3 | 0 | 1 | 4 |
| [src/music_kraken/target/__init__.py](/src/music_kraken/target/__init__.py) | Python | 4 | 0 | 2 | 6 |
| [src/music_kraken/target/set_target.py](/src/music_kraken/target/set_target.py) | Python | 37 | 7 | 18 | 62 |
| [src/music_kraken/utils/__init__.py](/src/music_kraken/utils/__init__.py) | Python | 1 | 1 | 1 | 3 |
| [src/music_kraken/utils/functions.py](/src/music_kraken/utils/functions.py) | Python | 3 | 0 | 1 | 4 |
| [src/music_kraken/utils/object_handeling.py](/src/music_kraken/utils/object_handeling.py) | Python | 19 | 0 | 6 | 25 |
| [src/music_kraken/utils/phonetic_compares.py](/src/music_kraken/utils/phonetic_compares.py) | Python | 39 | 2 | 17 | 58 |
| [src/music_kraken/utils/shared.py](/src/music_kraken/utils/shared.py) | Python | 61 | 3 | 9 | 73 |
| [src/music_kraken_cli.py](/src/music_kraken_cli.py) | Python | 94 | 9 | 32 | 135 |
| [src/music_kraken_gtk.py](/src/music_kraken_gtk.py) | Python | 3 | 0 | 2 | 5 |
| [src/test.db](/src/test.db) | Database | 92 | 0 | 0 | 92 |
| [src/try-programming-interface.py](/src/try-programming-interface.py) | Python | 14 | 98 | 22 | 134 |
| [src/try_python.py](/src/try_python.py) | Python | 13 | 1 | 6 | 20 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)