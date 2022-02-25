from flask import current_app, g, Flask, flash, jsonify, redirect, render_template, request, session, Response
import logging
import sqlite3
import json
import requests
from db import DB, KeyNotFound, BadRequest
import datetime

# how to set the logging level
logging.basicConfig(level=logging.ERROR)
# logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)

# Configure application
app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Needed to flash messages
app.secret_key = b'mEw6%7APK'

# path to database
DATABASE = 'splatDB.sqlite3'


# default path
@app.route('/')
def home():
    return render_template("home.html")


# hello world
@app.route('/hello')
def hello_world():
    data = {"message": "Hello, World!"}
    return jsonify(data)


# -----------------
# Create/Read Endpoints
# These JSON/REST api endpoints are used to add new records
# and return lookups based on Ids
# -------------------


# creates required table for application.
# note having a web endpoint for this is not a standard approach, but used for quick testing
@app.route('/create', methods=["GET"])
def create_tables():
    """
    Drops existing tables and creates new tables
    """
    db = DB(get_db_conn())
    return db.create_db('schema/create.sql')



@app.route('/album', methods=["POST"])
def add_album():
    """
    Loads a new appearance of song
    (and possibly a new song) into the database.
    """
    post_body = request.json
    if not post_body:
        logging.error("No post body")
        return Response(status=400)

    # get DB class with new connection
    db = DB(get_db_conn())

    try:
        resp = db.add_album(post_body)
        return resp, 201
    except BadRequest as e:
        raise InvalidUsage(e.message, status_code=e.error_code)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))


@app.route('/songs/<song_id>', methods=["GET"])
def find_song(song_id):
    """
    Returns a song's info
    (song_id, name, length, artist name, album name) based on song_id
    """
    # get DB class with new connection
    db = DB(get_db_conn())

    try:
        res = db.find_song(song_id)
        return jsonify(res)
    except KeyNotFound as e:
        logging.error(e)
        raise InvalidUsage(e.message, status_code=404)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))
    return Response(status=400)


@app.route('/songs/by_album/<album_id>', methods=["GET"])
def find_songs_by_album(album_id):
    """
    Returns all an album's songs
    (song_id, name, length, artist name, album name) based on album_id
    """
    # get DB class with new connection
    db = DB(get_db_conn())
    
    try:
        res = db.find_songs_by_album(album_id)
        return jsonify(res)
    except KeyNotFound as e:
        logging.error(e)
        raise InvalidUsage(e.message, status_code=404)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))
    return Response(status=400)


@app.route('/songs/by_artist/<artist_id>', methods=["GET"])
def find_songs_by_artist(artist_id):
    """
    Returns all an artists' songs
    (song_id, name, length, artist name, album name) based on artist_id
    """
    # get DB class with new connection
    db = DB(get_db_conn())

    try:
        res = db.find_songs_by_artist(artist_id)
        return jsonify(res)
    except KeyNotFound as e:
        logging.error(e)
        raise InvalidUsage(e.message, status_code=404)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))
    return Response(status=400)


@app.route('/albums/<album_id>', methods=["GET"])
def find_album(album_id):
    """
    Returns a album's info
    (album_id, album_name, release_year). 
    """
    # get DB class with new connection
    db = DB(get_db_conn())

    try:
        res = db.find_album(album_id)
        return jsonify(res)
    except KeyNotFound as e:
        logging.error(e)
        raise InvalidUsage(e.message, status_code=404)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))
    return Response(status=400)


@app.route('/albums/by_artist/<artist_id>', methods=["GET"])
def find_album_by_artist(artist_id):
    """
    Returns a album's info
    (album_id, album_name, release_year). 
    """
    # get DB class with new connection
    db = DB(get_db_conn())

    try:
        res = db.find_album_by_artist(artist_id)
        return jsonify(res)
    except KeyNotFound as e:
        logging.error(e)
        raise InvalidUsage(e.message, status_code=404)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))
    return Response(status=400)


@app.route('/artists/<artist_id>', methods=["GET"])
def find_artist(artist_id):
    """
    Returns a artist's info
    (artist_id, artist_name, country). 
    """
    # get DB class with new connection
    db = DB(get_db_conn())

    try:
        res = db.find_artist(artist_id)
        return jsonify(res)
    except KeyNotFound as e:
        logging.error(e)
        raise InvalidUsage(e.message, status_code=404)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))
    return Response(status=400)

# -----------------
# Analytics Endpoints
# These JSON/REST api endpoints are used to run analysis
# over the dataset and calculate an aggregated answer
# -------------------

@app.route('/analytics/artists/avg_song_length/<artist_id>', methods=["GET"])
def avg_song_length(artist_id):
    """
    Returns the average length of an artist's songs (artist_id, avg_length)
    """
    # get DB class with new connection
    db = DB(get_db_conn())

    try:
        res = db.avg_song_length(artist_id)
        return jsonify(res)
    except KeyNotFound as e:
        logging.error(e)
        raise InvalidUsage(e.message, status_code=404)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))
    return Response(status=400)


@app.route('/analytics/artists/top_length/<num_artists>', methods=["GET"])
def top_length(num_artists):
    """
    Returns top (n=num_artists) artists based on total length of songs
    (artist_id, total_length). 
    """
    # get DB class with new connection
    db = DB(get_db_conn())
    
    try:
        res = db.top_length(num_artists)
        return jsonify(res)
    except KeyNotFound as e:
        logging.error(e)
        raise InvalidUsage(e.message, status_code=404)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))
    return Response(status=400)


# -----------------
# Web APIs
# These simply wrap requests from the website/browser and
# invoke the underlying REST / JSON API.
# -------------------

# paste in a query
@app.route('/web/query', methods=["GET", "POST"])
def query():
    """
    runs pasted in query
    """

    data = None
    if request.method == "POST":
        qry = request.form.get("query")
        # Ensure query was submitted

        # get DB class with new connection
        db = DB(get_db_conn())

        # note DO NOT EVER DO THIS NORMALLY (run SQL from a client/web directly)
        # https://xkcd.com/327/
        try:
            res = db.run_query(str(qry))
        except sqlite3.Error as e:
            logging.error(e)
            return render_template("error.html", errmsg=str(e), errcode=400)

        data = res
    return render_template("query.html", data=data)

# paste in a query
@app.route('/web/post_data', methods=["GET", "POST"])
def post_song_web():
    """
    runs simple post song json
    """

    data = None
    if request.method == "POST":
        parameter = request.form.get("path")
        if parameter is None or parameter.strip() == "":
            flash("Must set key")
            return render_template("post_data.html", data=data)

        get_url = "http://127.0.0.1:5000/%s" % parameter
        print("Making request to %s" % get_url)
        # grab the response

        j = json.loads(request.form.get("json_data").strip())
        print("Json from form: %s" % j)
        r = requests.post(get_url, json=j)
        if r.status_code >= 400:
            print("Error.  %s  Body: %s" % (r, r.content))
            return render_template("error.html", errmsg=r.json(), errcode=r.status_code)

        else:
            flash("Ran post command")
        return render_template("post_data.html", data=None)
    return render_template("post_data.html", data=None)

@app.route('/web/create', methods=["GET"])
def create_web():
    get_url = "http://127.0.0.1:5000/create"
    print("Making request to %s" % get_url)
    # grab the response
    r = requests.get(get_url)
    if r.status_code >= 400:
        print("Error.  %s  Body: %s" % (r, r.content))
        return render_template("error.html", errmsg=r.json(), errcode=r.status_code)

    else:
        flash("Ran create command")
        data = r.json()
    return render_template("home.html", data=data)


@app.route('/web/songs', methods=["GET", "POST"])
def song_landing():
    data = None
    if request.method == "POST":
        path = request.form.get("path")

        parameter = request.form.get("parameter")
        if parameter is None or parameter.strip() == "":
            flash("Must set key")
            return render_template("songs.html", data=data)

        get_url = "http://127.0.0.1:5000/songs/" + path + parameter
        print("Making request to %s" % get_url)
        # grab the response
        r = requests.get(get_url)
        if r.status_code >= 400:
            print("Error.  %s  Body: %s" % (r, r.content))
            return render_template("error.html", errmsg=r.json(), errcode=r.status_code)

        else:
            data = r.json()
    return render_template("songs.html", data=data)


@app.route('/web/artists', methods=["GET", "POST"])
def artists_landing():
    data = None
    if request.method == "POST":
        path = request.form.get("path")
        # Ensure path was submitted

        parameter = request.form.get("parameter")
        if parameter is None or parameter.strip() == "":
            flash("Must set key")
            return render_template("artists.html", data=data)

        get_url = "http://127.0.0.1:5000/artists/" + path + parameter
        # grab the response
        r = requests.get(get_url)
        if r.status_code >= 400:
            print("Error.  %s  Body: %s" % (r, r.content))
            return render_template("error.html", errmsg=r.json(), errcode=r.status_code)

        else:
            data = r.json()
    return render_template("artists.html", data=data)


@app.route('/web/albums', methods=["GET", "POST"])
def albums_landing():
    data = None
    if request.method == "POST":
        path = request.form.get("path")
        # Ensure path was submitted

        parameter = request.form.get("parameter")
        if parameter is None or parameter.strip() == "":
            flash("Must set key")
            return render_template("albums.html", data=data)

        get_url = "http://127.0.0.1:5000/albums/" + path + parameter
        # grab the response
        r = requests.get(get_url)
        if r.status_code >= 400:
            print("Error.  %s  Body: %s" % (r, r.content))
            return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        else:
            data = r.json()
    return render_template("albums.html", data=data)


@app.route('/web/analytics', methods=["GET", "POST"])
def analytics_landing():
    data = None
    if request.method == "POST":
        path = request.form.get("path")
        # Ensure path was submitted

        if path == "solo_albums":
            get_url = "http://127.0.0.1:5000/analytics/" + path
        elif path == "playcount/top_song/" or path == "playcount/top_country/":
            date = request.form.get("date")
            if date is None or date.strip() == "":
                flash("Must set key")
                return render_template("analytics.html", data=data)

            get_url = "http://127.0.0.1:5000/analytics/" + path + date
        elif path == "playcount/top_source/":
            parameter = request.form.get("parameter")
            if parameter is None or parameter.strip() == "":
                flash("Must set key")
                return render_template("analytics.html", data=data)
            parameter2 = request.form.get("parameter2")
            if parameter2 is None or parameter2.strip() == "":
                flash("Must set key")
                return render_template("analytics.html", data=data)
            get_url = "http://127.0.0.1:5000/analytics/" + path + parameter + '/' + parameter2
        else:
            parameter = request.form.get("parameter")
            if parameter is None or parameter.strip() == "":
                flash("Must set key")
                return render_template("analytics.html", data=data)

            get_url = "http://127.0.0.1:5000/analytics/" + path + parameter

        # grab the response
        print(get_url)
        r = requests.get(get_url)
        if r.status_code >= 400:
            print("Error.  %s  Body: %s" % (r, r.content))
            return render_template("error.html", errmsg=r.json(), errcode=r.status_code)

        else:
            data = r.json()
    return render_template("analytics.html", data=data)


# -----------------
# Utilities / Errors
# -------------------

# gets connection to database
def get_db_conn():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    return db


# Error Class for managing Errors
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# called on close of response; closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# ########### post MS1 ############## #
