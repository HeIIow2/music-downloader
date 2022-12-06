CREATE TABLE Song
(
    id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    name    TEXT,
    isrc    TEXT,
    length  INT     -- length is in milliseconds (could be wrong)
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
    id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    song_id BIGINT,
    FOREIGN KEY(song_id) REFERENCES Song(id)
);

CREATE TABLE Target
(
    id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    file    TEXT NOT NULL,
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
