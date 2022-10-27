DROP TABLE IF EXISTS artist;
CREATE TABLE artist (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT
);

DROP TABLE IF EXISTS artist_release_group;
CREATE TABLE artist_release_group (
    artist_id TEXT NOT NULL,
    release_group_id TEXT NOT NULL
);

DROP TABLE IF EXISTS artist_track;
CREATE TABLE artist_track (
    artist_id TEXT NOT NULL,
    track_id TEXT NOT NULL
);

DROP TABLE IF EXISTS release_group;
CREATE TABLE release_group (
    id TEXT PRIMARY KEY NOT NULL,
    albumartist TEXT,
    albumsort INT,
    musicbrainz_albumtype TEXT,
    compilation TEXT
);

DROP TABLE IF EXISTS release_;
CREATE TABLE release_ (
    id TEXT PRIMARY KEY NOT NULL,
    release_group TEXT NOT NULL,
    name TEXT
);

DROP TABLE IF EXISTS track;
CREATE TABLE track (
    id TEXT PRIMARY KEY NOT NULL,
    release_id TEXT NOT NULL,
    name TEXT
);

