from music_kraken.objects import (
    Song,
    Album,
    Artist,
    Label,
    Source,
    DatabaseObject
)
from music_kraken.objects.collection import Collection
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


c = Collection([Song(title="hi"), Song(title="hi2"), Song(title="hi3")])
c1 = Collection([Song(title="he"), Song(title="hi5")])
c11 = Collection([Song(title="wow how ultra subby", isrc="hiii")])
c2 = Collection([Song(title="heeee")])

b = Collection([Song(title="some b"), Song(title="other b")])
b1 = Collection([Song(title="sub b")])
b11 = Collection([Song(title="This shouldn't work")])

b1.contain_collection_inside(b11)

b.contain_collection_inside(b1)
b.contain_collection_inside(c1)

c.contain_collection_inside(c1)
c.contain_collection_inside(c2)

c1.contain_collection_inside(c11)
c1.contain_collection_inside(c11)

print(c.data)
print(c1.data)

c.append(Song(title="after creation"))

other_song = Song(title="has same isrc", isrc="hiii", genre="hssss")
print(c.contains(other_song))
c11.append(other_song)
print(other_song)


print()
print(c.data, len(c))
print(c1.data)
print([(obj.genre or "various") + ":" + obj.title for obj in c.data])

print()
print("c: ", c)
print("b: ", b)

c.sync_with_other_collection(b)
print("synced: ")

print("c: ", c)
print("b: ", b)

print(c.data)
print(c._data)
