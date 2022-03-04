import logging
import sqlite3
from flask.cli import with_appcontext

# helper function that converts query result to json list, after cursor has executed a query
# this will not work for all endpoints direct, just the ones where you can translate
# a single query to the required json. 
def to_json(cursor):
    results = cursor.fetchall()
    headers = [d[0] for d in cursor.description]
    return [dict(zip(headers, row)) for row in results]


# Error class for when a key is not found
class KeyNotFound(Exception):
    def __init__(self, message=None):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = "Key/Id not found"

    def to_dict(self):
        rv = dict()
        rv['message'] = self.message
        return rv


# Error class for when request data is bad
class BadRequest(Exception):
    def __init__(self, message=None, error_code=400):
        Exception.__init__(self)
        if message:
            self.message = message
        else:
            self.message = "Bad Request"
        self.error_code = error_code

    def to_dict(self):
        rv = dict()
        rv['message'] = self.message
        return rv


"""
Wraps a single connection to the database with higher-level functionality.
Holds the DB connection
"""
class DB:
    def __init__(self, connection):
        self.conn = connection

    # Simple example of how to execute a query against the DB.
    # Again NEVER do this, you should only execute parameterized query
    # See https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.execute
    # This is the qmark style:
    # cur.execute("insert into people values (?, ?)", (who, age))
    # And this is the named style:
    # cur.execute("select * from people where name_last=:who and age=:age", {"who": who, "age": age})
    def run_query(self, query):
        c = self.conn.cursor()
        c.execute(query)
        res = to_json(c)
        self.conn.commit()
        return res

    # Run script that drops and creates all tables
    def create_db(self, create_file):
        print("Running SQL script file %s" % create_file)
        with open(create_file, "r") as f:
            self.conn.executescript(f.read())
        return "{\"message\":\"created\"}"

    # Add an album to the DB
    # An album has details, a list of artists, and a list of songs
    # If the artist or songs already exist then they should not be created
    # The album should be associated with the artists.  The order does not matter
    # Songs sould be associated with the album, the order *does* matter and should be retained.
    def add_album(self, post_body):
        try:
            album_id = post_body["album_id"]
            album_name = post_body["album_name"]
            release_year = post_body["release_year"]
            # An Artist is a dict of {"artist_id", "artist_name", "country" }
            # Arists is a list of artist [{"artist_id":12, "artist_name":"AA", "country":"XX"},{"arist_id": ...}]
            artists = post_body["artists"]
            # Songs is a list of { "song_id", "song_name", "length", "artist" }
            # Song Id an length are numbers, song_name is a string, artist is a list of artists (above)
            songs = post_body["songs"]
        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")
        if isinstance(songs, list) is False or isinstance(artists, list) is False:
            logging.error("song_ids or artist_ids are not lists")
            raise BadRequest("song_ids or artist_ids are not lists")
        c = self.conn.cursor()
        album_query = "INSERT OR IGNORE INTO album (album_id, album_name, release_year) VALUES (:album_id, :album_name, :release_year)"
        album_args = {"album_id": album_id, "album_name": album_name, "release_year":release_year}
        c.execute(album_query, album_args)
        if artists: 
            artist_query = "INSERT OR IGNORE INTO artist (artist_id, artist_name, country) VALUES (:artist_id, :artist_name, :country)"
            c.executemany(artist_query,artists) 
            artist_album_query = "INSERT INTO artist_album (artist_id, album_id) VALUES (:artist_id, :album_id)"
            artist_album_vals = map(lambda artist: {'artist_id': artist['artist_id'], 'album_id': album_id}, artists)
            c.executemany(artist_album_query, artist_album_vals)
        if songs:
            song_query = "INSERT OR IGNORE INTO song (song_id, song_name, length) VALUES (:song_id, :song_name, :length)"
            c.executemany(song_query, songs)
            song_album_query = "INSERT INTO song_album (song_id, album_id, order_in_album) VALUES (:song_id, :album_id, :order_in_album)"
            song_album_vals = [{'song_id': song['song_id'], 'album_id': album_id, 'order_in_album': i+1} for i,song in enumerate(songs)] 
            print(song_album_vals)
            c.executemany(song_album_query, song_album_vals)
        self.conn.commit()
        return "{\"message\":\"album inserted\"}"

    """
    Returns a song's info
    raise KeyNotFound() if song_id is not found
    """
    def find_song(self, song_id):
        c = self.conn.cursor()
        song_query = "SELECT song_id, song_name, length FROM song WHERE song_id =:song_id"
        c.execute(song_query, {'song_id':song_id})
        res = to_json(c)
        length = len(list(res))
        if length==0:
            raise KeyNotFound()
        song_artist_query = "SELECT artist_id FROM song_artist WHERE song_id = :id ORDER BY artist_id"
        song_artist_val = {"id": res[0]["song_id"]}
        c.execute(song_artist_query,song_artist_val)
        artist_ids = [x[0] for x in c.fetchall()]
        res[0]["artist_ids"] = artist_ids
        song_album_query = "SELECT album_id FROM song_album WHERE song_id = :id ORDER BY album_id"
        song_album_val = {"id": res[0]["song_id"]}
        c.execute(song_album_query, song_album_val)
        album_ids = [x[0] for x in c.fetchall()] 
        res[0]["album_ids"] = album_ids
        self.conn.commit()
        return res

    """
    Returns all an album's songs
    raise KeyNotFound() if album_id not found
    """
    def find_songs_by_album(self, album_id):
        c = self.conn.cursor()
        album_query = "SELECT * from album WHERE album_id = :id"
        album_vals = {'id', album_id}
        c.execute(album_query, album_vals)
        if not c.fetchall():
            raise KeyNotFound()
        song_album_query = """SELECT song_id, song_name, length, album_name FROM song 
        NATURAL JOIN album NATURAL JOIN song_album 
        WHERE album_id =:id ORDER BY order_in_album;"""
        c.execute(song_album_query, album_vals)
        res = to_json(c)
        length = len(list(res))
        if length == 0:
            raise KeyNotFound()
        song_artist_query = "SELECT artist_id FROM song_artist WHERE song_id = :song_id ORDER BY artist_id"
        for song in res:
            c.execute(song_artist_query, {'song_id': song['song_id']})
            song['artist_ids'] =[x[0] for x in c.fetchall()]
        self.conn.commit()
        return res

    
    """
    Returns all an artists' songs
    raise KeyNotFound() if artist_id is not found
    """
    def find_songs_by_artist(self, artist_id):
        c = self.conn.cursor()
        # checking if artist exists
        artist_query = "SELECT * from artist WHERE artist_id = :artist_id;"
        artist_val = {'artist_id':artist_id}
        c.execute(artist_query,artist_val)
        fetch = c.fetchall()
        if not fetch:
            raise KeyNotFound()
        # fetching songs for artist
        song_query = """SELECT song_id, song_name, length  
            FROM song NATURAL JOIN song_artist NATURAL JOIN artist 
            WHERE artist_id =:artist_id ORDER BY song_id;"""
        c.execute(song_query, artist_val)
        res = to_json(c)
        # no songs for artist
        if len(list(res)) ==0:
            raise KeyNotFound()
        # adding artist ids
        for song in res:
            song_artist_query = "SELECT artist_id FROM song_artist WHERE song_id = :song_id ORDER BY artist_id"
            song_artist_val = {"song_id": song["song_id"]}
            c.execute(song_artist_query,song_artist_val )
            song["artist_ids"] = [x[0] for x in c.fetchall()]
        self.conn.commit()
        return res
   
    """
    Returns a album's info
    raise KeyNotFound() if album_id is not found
    """
    def find_album(self, album_id):
        c = self.conn.cursor()
        # check if album exists
        album_id_query = "SELECT * from album WHERE album_id = :album_id;"
        album_id_val = {'album_id': album_id}
        c.execute(album_id_query,album_id_val)
        exists = c.fetchall()
        if not exists:
            raise KeyNotFound()
        # retrieve album 
        album_query = "SELECT album_id, album_name, release_year FROM album WHERE album_id = :album_id;"
        c.execute(album_query, album_id_val)
        res = to_json(c)
        # get artist id 
        artist_id_query = "SELECT artist_id FROM artist_album WHERE album_id = :album_id ORDER BY artist_id"
        album_id_val2 = {"album_id": res[0]["album_id"]}
        c.execute(artist_id_query,album_id_val2)
        res[0]["artist_ids"] = [x[0] for x in c.fetchall()] 
        # get song id 
        song_id_query = "SELECT song_id FROM song_album WHERE album_id = :album_id ORDER BY order_in_album"
        c.execute(song_id_query, album_id_val2)
        res[0]["song_ids"] = [x[0] for x in c.fetchall()] 

        self.conn.commit()
        return res

    """
    # not me 
    Returns a album's info
    raise KeyNotFound() if artist_id is not found 
    if artist exist, but there are no albums then return an empty result (from to_json)
    """
    def find_album_by_artist(self, artist_id):
        c = self.conn.cursor()
        # TODO milestone splat
        res = to_json(c)
        self.conn.commit()
        return res

    """
    Returns a artist's info
    raise KeyNotFound() if artist_id is not found 
    """
    # not me 
    def find_artist(self, artist_id):
        c = self.conn.cursor()
        c.execute("""SELECT artist_id, artist_name, country FROM artist WHERE artist_id = ?;""", (artist_id,))
        res = to_json(c)
        if not len(list(res)):
            raise KeyNotFound()
        self.conn.commit()
        return res

    """
    Returns the average length of an artist's songs (artist_id, avg_length)
    raise KeyNotFound() if artist_id is not found 
    """
    def avg_song_length(self, artist_id):
        c = self.conn.cursor()
        #check if artist exsits
        artist_id_query = "SELECT * from artist WHERE artist_id = :artist_id;"
        artist_id_val = {'artist_id': artist_id}
        c.execute(artist_id_query, artist_id_val)
        exists = c.fetchall()
        if not exists:
            raise KeyNotFound()
        length_query ="""SELECT artist_id, avg(length) AS avg_length
            FROM song NATURAL JOIN artist NATURAL JOIN song_artist 
            WHERE artist_id = :artist_id;"""
        c.execute(length_query, artist_id_val)
        res = to_json(c)
        self.conn.commit()
        return res


#not me 
    """
    Returns top (n=num_artists) artists based on total length of songs
    """
    def top_length(self, num_artists):
        c = self.conn.cursor()
        # TODO milestone splat
        res = to_json(c)
        self.conn.commit()
        return res
