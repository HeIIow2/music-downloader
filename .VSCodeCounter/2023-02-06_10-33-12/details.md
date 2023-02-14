# Details

Date : 2023-02-06 10:33:12

Directory /home/lars/Projects/music-downloader/src

Total : 50 files,  3575 codes, 775 comments, 1028 blanks, all 5378 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [src/__init__.py](/src/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/create_custom_objects.py](/src/create_custom_objects.py) | Python | 80 | 3 | 18 | 101 |
| [src/metal_archives.py](/src/metal_archives.py) | Python | 45 | 6 | 17 | 68 |
| [src/music_kraken/__init__.py](/src/music_kraken/__init__.py) | Python | 63 | 26 | 33 | 122 |
| [src/music_kraken/__main__.py](/src/music_kraken/__main__.py) | Python | 3 | 2 | 3 | 8 |
| [src/music_kraken/database/__init__.py](/src/music_kraken/database/__init__.py) | Python | 18 | 0 | 5 | 23 |
| [src/music_kraken/database/database.py](/src/music_kraken/database/old_database.py) | Python | 429 | 112 | 111 | 652 |
| [src/music_kraken/database/objects/__init__.py](/src/music_kraken/objects/__init__.py) | Python | 20 | 0 | 7 | 27 |
| [src/music_kraken/database/objects/artist.py](/src/music_kraken/objects/artist.py) | Python | 18 | 0 | 5 | 23 |
| [src/music_kraken/database/objects/formatted_text.py](/src/music_kraken/objects/formatted_text.py) | Python | 48 | 57 | 16 | 121 |
| [src/music_kraken/database/objects/metadata.py](/src/music_kraken/objects/metadata.py) | Python | 251 | 68 | 61 | 380 |
| [src/music_kraken/database/objects/parents.py](/src/music_kraken/objects/parents.py) | Python | 40 | 8 | 19 | 67 |
| [src/music_kraken/database/objects/song.py](/src/music_kraken/objects/song.py) | Python | 323 | 64 | 85 | 472 |
| [src/music_kraken/database/objects/source.py](/src/music_kraken/objects/source.py) | Python | 116 | 38 | 41 | 195 |
| [src/music_kraken/database/temp_database.py](/src/music_kraken/database/temp_database.py) | Python | 12 | 0 | 8 | 20 |
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
| [src/music_kraken/static_files/new_db.sql](/src/music_kraken/static_files/new_db.sql) | SQLite | 72 | 0 | 10 | 82 |
| [src/music_kraken/static_files/temp_database_structure.sql](/src/music_kraken/static_files/temp_database_structure.sql) | SQLite | 135 | 0 | 10 | 145 |
| [src/music_kraken/tagging/__init__.py](/src/music_kraken/tagging/__init__.py) | Python | 8 | 0 | 2 | 10 |
| [src/music_kraken/tagging/id3.py](/src/music_kraken/tagging/id3.py) | Python | 51 | 4 | 20 | 75 |
| [src/music_kraken/target/__init__.py](/src/music_kraken/target/__init__.py) | Python | 4 | 0 | 2 | 6 |
| [src/music_kraken/target/set_target.py](/src/music_kraken/target/set_target.py) | Python | 37 | 7 | 18 | 62 |
| [src/music_kraken/utils/__init__.py](/src/music_kraken/utils/__init__.py) | Python | 1 | 1 | 1 | 3 |
| [src/music_kraken/utils/functions.py](/src/music_kraken/utils/functions.py) | Python | 3 | 0 | 1 | 4 |
| [src/music_kraken/utils/object_handeling.py](/src/music_kraken/utils/object_handeling.py) | Python | 19 | 0 | 6 | 25 |
| [src/music_kraken/utils/phonetic_compares.py](/src/music_kraken/utils/phonetic_compares.py) | Python | 39 | 2 | 17 | 58 |
| [src/music_kraken/utils/shared.py](/src/music_kraken/utils/shared.py) | Python | 62 | 3 | 10 | 75 |
| [src/music_kraken/utils/string_processing.py](/src/music_kraken/utils/string_processing.py) | Python | 2 | 5 | 2 | 9 |
| [src/music_kraken_cli.py](/src/music_kraken_cli.py) | Python | 91 | 9 | 32 | 132 |
| [src/music_kraken_gtk.py](/src/music_kraken_gtk.py) | Python | 3 | 0 | 2 | 5 |
| [src/test.db](/src/test.db) | Database | 91 | 0 | 1 | 92 |
| [src/try-programming-interface.py](/src/try-programming-interface.py) | Python | 14 | 98 | 22 | 134 |
| [src/try_python.py](/src/try_python.py) | Python | 13 | 1 | 6 | 20 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)