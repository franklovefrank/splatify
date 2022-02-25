import logging
import sqlite3

# helper function that converts query result to json list, after cursor has executed a query
# this will not work for all endpoints directly, just the ones where you can translate
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

    # Run script that drops and creates all tables
    def create_db(self, create_file):
        print("Running SQL script file %s" % create_file)
        with open(create_file, "r") as f:
            self.conn.executescript(f.read())
        return {"message": "created"}


    # Add a new test record from a json object
    def add_test(self, post_body):
        try:
            field1 = post_body["field1"]
            field2 = post_body["field2"]
        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

        c = self.conn.cursor()

        # one way of executing query with ? and a list
        insert_test = """INSERT INTO test_table (field1, field2)
                        VALUES (?, ?)"""
        c.execute(insert_test, [field1, field2])
        self.conn.commit()

        return {"message":"test added inserted"}
        

    """
    Returns a test record info
    adds a field "count" that counts up from field2 3 times
    raise KeyNotFound() if field1 is not found
    """
    def find_test(self, id):
        c = self.conn.cursor()

        # Another way of executing a query with named parameters
        query = """
            select field1, field2 from test_table where field1 = :id
           """
        c.execute(query, {"id": id})
        res = to_json(c)
        self.conn.commit()
        # If fetchmany in to_json had no records...
        if len(res) == 0:
            raise KeyNotFound(message="Field1 %s not found" % id)
        # to_json makes a list, get the first record. 
        first_record = res[0] 
        # get the field to create the "list" from
        start_number = first_record["field2"] 
        # make a list and add it into the record 
        first_record["count"] = [x for x in range(start_number,start_number+4) ]
        return first_record


    """
    Returns all test records
    """
    def all_tests(self,):
        c = self.conn.cursor()
        query = """
            select field1, field2 from test_table
           """
        c.execute(query)
        res = to_json(c)
        self.conn.commit()
        return res
