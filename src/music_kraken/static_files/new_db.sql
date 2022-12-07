CREATE TABLE Song
(
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        TEXT,
    isrc        TEXT,
    length      INT,    -- length is in milliseconds (could be wrong)
    album_id    BIGINT,
    FOREIGN KEY(album_id) REFERENCES Album(id)
);


CREATE TABLE Source
(
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    src         TEXT NOT NULL,
    url         TEXT NOT NULL,
    certainty   INT NOT NULL DEFAULT 0,   -- certainty=0 -> it is definitely a valid source
    valid       BOOLEAN NOT NULL DEFAULT 1,
    song_id     BIGINT,
    FOREIGN KEY(song_id) REFERENCES Song(id)
);

CREATE TABLE Artist
(
    id      INTEGER AUTO_INCREMENT PRIMARY KEY, 
    name    TEXT
);


CREATE TABLE Album
(
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    title           TEXT, 
    copyright       TEXT,
    album_status    TEXT,
    language        TEXT,
    year            TEXT,
    date            TEXT,
    country         TEXT,
    barcode         TEXT
);

CREATE TABLE Target
(
    id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    file    TEXT,
    path    TEXT,
    song_id BIGINT UNIQUE,
    FOREIGN KEY(song_id) REFERENCES Song(id)
);

CREATE TABLE Lyrics
(
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    text        TEXT,
    language    TEXT,
    song_id     BIGINT,
    FOREIGN KEY(song_id) REFERENCES Song(id)
);

CREATE TABLE SongArtist
(
      song_id   BIGINT,
      artist_id INTEGER,
      FOREIGN KEY(song_id) REFERENCES Song(id),
      FOREIGN KEY(artist_id) REFERENCES Artist(id)
);

CREATE TABLE AlbumArtist
(
      album_id   BIGINT,
      artist_id INTEGER,
      FOREIGN KEY(album_id) REFERENCES Album(id),
      FOREIGN KEY(artist_id) REFERENCES Artist(id)
);
