# Details

Date : 2023-06-14 07:47:51

Directory /home/lars/Projects/music-downloader/src

Total : 83 files,  5827 codes, 1152 comments, 1825 blanks, all 8804 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [src/__init__.py](/src/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/actual_donwload.py](/src/actual_donwload.py) | Python | 16 | 0 | 6 | 22 |
| [src/create_custom_objects.py](/src/create_custom_objects.py) | Python | 58 | 0 | 6 | 64 |
| [src/metal_archives.py](/src/metal_archives.py) | Python | 30 | 0 | 12 | 42 |
| [src/music_kraken/__init__.py](/src/music_kraken/__init__.py) | Python | 112 | 6 | 33 | 151 |
| [src/music_kraken/__main__.py](/src/music_kraken/__main__.py) | Python | 98 | 3 | 23 | 124 |
| [src/music_kraken/audio/__init__.py](/src/music_kraken/audio/__init__.py) | Python | 7 | 0 | 3 | 10 |
| [src/music_kraken/audio/codec.py](/src/music_kraken/audio/codec.py) | Python | 25 | 0 | 8 | 33 |
| [src/music_kraken/audio/metadata.py](/src/music_kraken/audio/metadata.py) | Python | 60 | 4 | 24 | 88 |
| [src/music_kraken/cli/__init__.py](/src/music_kraken/cli/__init__.py) | Python | 2 | 0 | 0 | 2 |
| [src/music_kraken/cli/download/__init__.py](/src/music_kraken/cli/download/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/music_kraken/cli/download/shell.py](/src/music_kraken/cli/download/shell.py) | Python | 199 | 86 | 78 | 363 |
| [src/music_kraken/cli/options/__init__.py](/src/music_kraken/cli/options/__init__.py) | Python | 3 | 0 | 1 | 4 |
| [src/music_kraken/cli/options/invidious/__init__.py](/src/music_kraken/cli/options/invidious/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/music_kraken/cli/options/invidious/shell.py](/src/music_kraken/cli/options/invidious/shell.py) | Python | 66 | 7 | 28 | 101 |
| [src/music_kraken/connection/__init__.py](/src/music_kraken/connection/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [src/music_kraken/connection/connection.py](/src/music_kraken/connection/connection.py) | Python | 168 | 1 | 30 | 199 |
| [src/music_kraken/connection/rotating.py](/src/music_kraken/connection/rotating.py) | Python | 27 | 3 | 14 | 44 |
| [src/music_kraken/database/__init__.py](/src/music_kraken/database/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/music_kraken/database/data_models.py](/src/music_kraken/database/data_models.py) | Python | 122 | 24 | 52 | 198 |
| [src/music_kraken/database/database.py](/src/music_kraken/database/database.py) | Python | 104 | 47 | 38 | 189 |
| [src/music_kraken/download/__init__.py](/src/music_kraken/download/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [src/music_kraken/download/multiple_options.py](/src/music_kraken/download/multiple_options.py) | Python | 69 | 0 | 31 | 100 |
| [src/music_kraken/download/page_attributes.py](/src/music_kraken/download/page_attributes.py) | Python | 67 | 1 | 29 | 97 |
| [src/music_kraken/download/results.py](/src/music_kraken/download/results.py) | Python | 62 | 7 | 26 | 95 |
| [src/music_kraken/download/search.py](/src/music_kraken/download/search.py) | Python | 124 | 24 | 56 | 204 |
| [src/music_kraken/objects/__init__.py](/src/music_kraken/objects/__init__.py) | Python | 14 | 0 | 5 | 19 |
| [src/music_kraken/objects/cache.py](/src/music_kraken/objects/cache.py) | Python | 37 | 56 | 18 | 111 |
| [src/music_kraken/objects/collection.py](/src/music_kraken/objects/collection.py) | Python | 91 | 31 | 39 | 161 |
| [src/music_kraken/objects/formatted_text.py](/src/music_kraken/objects/formatted_text.py) | Python | 50 | 10 | 19 | 79 |
| [src/music_kraken/objects/lyrics.py](/src/music_kraken/objects/lyrics.py) | Python | 25 | 0 | 7 | 32 |
| [src/music_kraken/objects/metadata.py](/src/music_kraken/objects/metadata.py) | Python | 272 | 62 | 63 | 397 |
| [src/music_kraken/objects/option.py](/src/music_kraken/objects/option.py) | Python | 28 | 0 | 13 | 41 |
| [src/music_kraken/objects/parents.py](/src/music_kraken/objects/parents.py) | Python | 71 | 35 | 35 | 141 |
| [src/music_kraken/objects/song.py](/src/music_kraken/objects/song.py) | Python | 480 | 113 | 120 | 713 |
| [src/music_kraken/objects/source.py](/src/music_kraken/objects/source.py) | Python | 93 | 16 | 33 | 142 |
| [src/music_kraken/objects/target.py](/src/music_kraken/objects/target.py) | Python | 65 | 15 | 24 | 104 |
| [src/music_kraken/pages/__init__.py](/src/music_kraken/pages/__init__.py) | Python | 4 | 0 | 2 | 6 |
| [src/music_kraken/pages/abstract.py](/src/music_kraken/pages/abstract.py) | Python | 234 | 46 | 93 | 373 |
| [src/music_kraken/pages/encyclopaedia_metallum.py](/src/music_kraken/pages/encyclopaedia_metallum.py) | Python | 432 | 90 | 127 | 649 |
| [src/music_kraken/pages/musify.py](/src/music_kraken/pages/musify.py) | Python | 576 | 275 | 166 | 1,017 |
| [src/music_kraken/pages/preset.py](/src/music_kraken/pages/preset.py) | Python | 47 | 1 | 17 | 65 |
| [src/music_kraken/pages/youtube.py](/src/music_kraken/pages/youtube.py) | Python | 254 | 45 | 79 | 378 |
| [src/music_kraken/static_files/new_db.sql](/src/music_kraken/static_files/new_db.sql) | SQLite | 72 | 0 | 10 | 82 |
| [src/music_kraken/static_files/temp_database_structure.sql](/src/music_kraken/static_files/temp_database_structure.sql) | SQLite | 135 | 0 | 10 | 145 |
| [src/music_kraken/utils/__init__.py](/src/music_kraken/utils/__init__.py) | Python | 2 | 1 | 2 | 5 |
| [src/music_kraken/utils/config/__init__.py](/src/music_kraken/utils/config/__init__.py) | Python | 7 | 0 | 4 | 11 |
| [src/music_kraken/utils/config/audio.py](/src/music_kraken/utils/config/audio.py) | Python | 152 | 15 | 28 | 195 |
| [src/music_kraken/utils/config/base_classes.py](/src/music_kraken/utils/config/base_classes.py) | Python | 136 | 35 | 61 | 232 |
| [src/music_kraken/utils/config/config.py](/src/music_kraken/utils/config/config.py) | Python | 92 | 16 | 30 | 138 |
| [src/music_kraken/utils/config/connection.py](/src/music_kraken/utils/config/connection.py) | Python | 80 | 2 | 15 | 97 |
| [src/music_kraken/utils/config/logging.py](/src/music_kraken/utils/config/logging.py) | Python | 104 | 4 | 17 | 125 |
| [src/music_kraken/utils/config/misc.py](/src/music_kraken/utils/config/misc.py) | Python | 40 | 0 | 9 | 49 |
| [src/music_kraken/utils/config/paths.py](/src/music_kraken/utils/config/paths.py) | Python | 40 | 0 | 13 | 53 |
| [src/music_kraken/utils/enums/__init__.py](/src/music_kraken/utils/enums/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/music_kraken/utils/enums/album.py](/src/music_kraken/utils/enums/album.py) | Python | 16 | 6 | 5 | 27 |
| [src/music_kraken/utils/enums/source.py](/src/music_kraken/utils/enums/source.py) | Python | 40 | 1 | 8 | 49 |
| [src/music_kraken/utils/exception/__init__.py](/src/music_kraken/utils/exception/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [src/music_kraken/utils/exception/config.py](/src/music_kraken/utils/exception/config.py) | Python | 14 | 8 | 7 | 29 |
| [src/music_kraken/utils/exception/download.py](/src/music_kraken/utils/exception/download.py) | Python | 8 | 0 | 4 | 12 |
| [src/music_kraken/utils/functions.py](/src/music_kraken/utils/functions.py) | Python | 3 | 0 | 1 | 4 |
| [src/music_kraken/utils/object_handeling.py](/src/music_kraken/utils/object_handeling.py) | Python | 19 | 0 | 6 | 25 |
| [src/music_kraken/utils/path_manager/__init__.py](/src/music_kraken/utils/path_manager/__init__.py) | Python | 2 | 0 | 2 | 4 |
| [src/music_kraken/utils/path_manager/config_directory.py](/src/music_kraken/utils/path_manager/config_directory.py) | Python | 4 | 0 | 4 | 8 |
| [src/music_kraken/utils/path_manager/locations.py](/src/music_kraken/utils/path_manager/locations.py) | Python | 16 | 0 | 9 | 25 |
| [src/music_kraken/utils/path_manager/music_directory.py](/src/music_kraken/utils/path_manager/music_directory.py) | Python | 36 | 9 | 14 | 59 |
| [src/music_kraken/utils/phonetic_compares.py](/src/music_kraken/utils/phonetic_compares.py) | Python | 39 | 2 | 17 | 58 |
| [src/music_kraken/utils/regex.py](/src/music_kraken/utils/regex.py) | Python | 1 | 0 | 2 | 3 |
| [src/music_kraken/utils/shared.py](/src/music_kraken/utils/shared.py) | Python | 66 | 22 | 22 | 110 |
| [src/music_kraken/utils/string_processing.py](/src/music_kraken/utils/string_processing.py) | Python | 16 | 5 | 11 | 32 |
| [src/music_kraken/utils/support_classes/__init__.py](/src/music_kraken/utils/support_classes/__init__.py) | Python | 4 | 0 | 1 | 5 |
| [src/music_kraken/utils/support_classes/default_target.py](/src/music_kraken/utils/support_classes/default_target.py) | Python | 56 | 0 | 15 | 71 |
| [src/music_kraken/utils/support_classes/download_result.py](/src/music_kraken/utils/support_classes/download_result.py) | Python | 69 | 0 | 21 | 90 |
| [src/music_kraken/utils/support_classes/query.py](/src/music_kraken/utils/support_classes/query.py) | Python | 24 | 0 | 9 | 33 |
| [src/music_kraken/utils/support_classes/thread_classes.py](/src/music_kraken/utils/support_classes/thread_classes.py) | Python | 8 | 0 | 4 | 12 |
| [src/music_kraken_cli.py](/src/music_kraken_cli.py) | Python | 3 | 0 | 3 | 6 |
| [src/music_kraken_gtk.py](/src/music_kraken_gtk.py) | Python | 3 | 0 | 2 | 5 |
| [src/musify_search.py](/src/musify_search.py) | Python | 38 | 0 | 14 | 52 |
| [src/tests/__init__.py](/src/tests/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/tests/conftest.py](/src/tests/conftest.py) | Python | 3 | 1 | 2 | 6 |
| [src/tests/test_building_objects.py](/src/tests/test_building_objects.py) | Python | 81 | 1 | 13 | 95 |
| [src/tests/test_download.py](/src/tests/test_download.py) | Python | 30 | 1 | 12 | 43 |
| [src/tests/test_objects.py](/src/tests/test_objects.py) | Python | 173 | 15 | 51 | 239 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)