DROP TABLE IF EXISTS album;
DROP TABLE IF EXISTS artist;
DROP TABLE IF EXISTS song;
DROP TABLE IF EXISTS song_artist;
DROP TABLE IF EXISTS song_album;
DROP TABLE IF EXISTS artist_album;

CREATE TABLE album (
    album_id INT,
    album_name VARCHAR(40) NOT NULL,
    release_year YEAR,
    PRIMARY KEY (album_id)
);

CREATE TABLE artist (
    artist_id INT,
    artist_name VARCHAR(60) NOT NULL,
    country VARCHAR(60),
    PRIMARY KEY (artist_id)
);

CREATE TABLE song (
    song_id INT,
    song_name VARCHAR(60) NOT NULL,
    length SMALLINT,
    PRIMARY KEY (song_id)
);

CREATE TABLE song_artist (
    song_id INT NOT NULL,
    artist_id INT NOT NULL,
    FOREIGN KEY (artist_id) REFERENCES artist,
    FOREIGN KEY (song_id) REFERENCES song,
    PRIMARY KEY (song_id, artist_id)
);

CREATE TABLE song_album (
    song_id INT NOT NULL,
    album_id INT NOT NULL,
    order_in_album INT NOT NULL,
    FOREIGN KEY (album_id) REFERENCES album,
    FOREIGN KEY (song_id) REFERENCES song
);

CREATE TABLE artist_album (
    artist_id INT NOT NULL,
    album_id INT NOT NULL,
    FOREIGN KEY (artist_id) REFERENCES artist,
    FOREIGN KEY (album_id) REFERENCES album
);
