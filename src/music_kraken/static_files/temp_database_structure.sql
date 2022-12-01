DROP TABLE IF EXISTS artist;
CREATE TABLE artist (
    id TEXT PRIMARY KEY NOT NULL,
    mb_id TEXT,
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
    compilation TEXT,
    album_artist_id TEXT
);

DROP TABLE IF EXISTS release_;
CREATE TABLE release_ (
    id TEXT PRIMARY KEY NOT NULL,
    release_group_id TEXT NOT NULL,
    title TEXT, 
    copyright TEXT,
    album_status TEXT,
    language TEXT,
    year TEXT,
    date TEXT,
    country TEXT,
    barcode TEXT
);

DROP TABLE IF EXISTS track;
CREATE TABLE track (
    id TEXT PRIMARY KEY NOT NULL,
    downloaded BOOLEAN NOT NULL DEFAULT 0,
    release_id TEXT NOT NULL,
    mb_id TEXT,
    track TEXT,
    length INT,
    tracknumber TEXT,
    isrc TEXT,
    genre TEXT,
    lyrics TEXT,
    path TEXT,
    file TEXT,
    url TEXT,
    src TEXT
);

DROP TABLE IF EXISTS lyrics;
CREATE TABLE lyrics (
    track_id TEXT NOT NULL,
    text TEXT,
    language TEXT
);

DROP TABLE IF EXISTS target;
CREATE TABLE target (
    track_id TEXT NOT NULL,
    file TEXT,
    path TEXT
);

DROP TABLE IF EXISTS source;
CREATE TABLE source (
    track_id TEXT NOT NULL,
    src TEXT NOT NULL,
    url TEXT NOT NULL,
    certainty INT NOT NULL DEFAULT 0,   -- certainty=0 -> it is definitly a valid source
    valid BOOLEAN NOT NULL DEFAULT 1
);

DROP TABLE IF EXISTS easy_id3;
CREATE TABLE easy_id3 ();
