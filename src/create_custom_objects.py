from music_kraken.objects import (
    Song,
    Album,
    Artist,
    Label,
    Source,
    DatabaseObject
)
from music_kraken.utils.enums import SourcePages


only_smile = Artist(
    name="Only Smile",
    source_list=[Source(SourcePages.BANDCAMP, "https://onlysmile.bandcamp.com/")],
    main_album_list=[
        Album(
            title="Few words...",
            source_list=[Source(SourcePages.BANDCAMP, "https://onlysmile.bandcamp.com/album/few-words")],
            song_list=[
                Song(title="Everything will be fine"),
                Song(title="Only Smile"),
                Song(title="Dear Diary"),
                Song(title="Sad Story")
            ],
            artist_list=[
                Artist(
                    name="Only Smile",
                    source_list=[Source(SourcePages.BANDCAMP, "https://onlysmile.bandcamp.com/")],
                    main_album_list=[
                        Album(
                            title="Few words...",
                            source_list=[Source(SourcePages.BANDCAMP, "https://onlysmile.bandcamp.com/album/few-words")],
                            song_list=[
                                Song(title="Everything will be fine"),
                                Song(title="Only Smile"),
                                Song(title="Dear Diary"),
                                Song(title="Sad Story")
                            ],
                            artist_list=[
                                Artist(
                                    name="Only Smile",
                                    source_list=[Source(SourcePages.BANDCAMP, "https://onlysmile.bandcamp.com/")]
                                )
                            ]
                        ),
                        Album(
                            title="Your best friend",
                            source_list=[Source(SourcePages.BANDCAMP, "https://onlysmile.bandcamp.com/album/your-best-friend")]
                        )
                    ]
                ),
                Artist(
                    name="Only Smile",
                    source_list=[Source(SourcePages.BANDCAMP, "https://onlysmile.bandcamp.com/")],
                    main_album_list=[
                        Album(
                            title="Few words...",
                            source_list=[Source(SourcePages.BANDCAMP, "https://onlysmile.bandcamp.com/album/few-words")],
                            song_list=[
                                Song(title="Everything will be fine"),
                                Song(title="Only Smile"),
                                Song(title="Dear Diary"),
                                Song(title="Sad Story")
                            ],
                            artist_list=[
                                Artist(
                                    name="Only Smile",
                                    source_list=[Source(SourcePages.BANDCAMP, "https://onlysmile.bandcamp.com/")]
                                )
                            ]
                        ),
                        Album(
                            title="Your best friend",
                            source_list=[Source(SourcePages.BANDCAMP, "https://onlysmile.bandcamp.com/album/your-best-friend")]
                        )
                    ]
                )
            ]
        ),
        Album(
            title="Your best friend",
            source_list=[Source(SourcePages.BANDCAMP, "https://onlysmile.bandcamp.com/album/your-best-friend")]
        )
    ]
)


objects_by_id = {}

def add_to_objects_dump(db_obj: DatabaseObject):
    objects_by_id[db_obj.id] = db_obj

    for collection in db_obj.all_collections:
        for new_db_obj in collection:
            if new_db_obj.id not in objects_by_id:
                add_to_objects_dump(new_db_obj)


add_to_objects_dump(only_smile)

for _id, _object in objects_by_id.items():
    print(_id, _object, sep=": ")

print(only_smile)
