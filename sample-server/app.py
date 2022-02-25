from flask import current_app, g, Flask, flash, jsonify, redirect, render_template, request, session, Response
import logging
import sqlite3
import json
import requests
from db import DB, KeyNotFound, BadRequest
import datetime

# Configure application
app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Needed to flash messages
app.secret_key = b'mEw6%7APE'

# path to database
DATABASE = 'testDB.sqlite3'

# how to set the logging level
# logging.basicConfig(level=logging.ERROR)
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

# hello world
@app.route('/')
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
    return jsonify(db.create_db('schema/create.sql'))


# Take a new test object POSTed as a JSON
@app.route('/new', methods=["POST"])
def add_test():
    """
    Loads a new test record 
    """
    post_body = request.json
    if not post_body:
        logging.error("No post body")
        return Response(status=400)

    # get DB class with new connection
    db = DB(get_db_conn())

    try:
        # add a record via the DB class
        resp = db.add_test(post_body)
        logging.info("Response : %s" % resp)
        return resp, 201
    except BadRequest as e:
        raise InvalidUsage(e.message, status_code=e.error_code)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))


# Return all Test items
@app.route('/test', methods=["GET"])
def all_tests():
    """
    Returns all test record
    """
    # get DB class with new connection
    db = DB(get_db_conn())

    try:
        res = db.all_tests()
        return jsonify(res)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))

# Find one particular test record and add an array of counting 
# 3 from field2
@app.route('/test/<id>', methods=["GET"])
def find_test(id):
    """
    Returns a test record
    """
    # get DB class with new connection
    db = DB(get_db_conn())

    try:
        res = db.find_test(id)
        return jsonify(res)
    except KeyNotFound as e:
        logging.error(e)
        raise InvalidUsage(e.message, status_code=404)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))
    return Response(status=400)


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

