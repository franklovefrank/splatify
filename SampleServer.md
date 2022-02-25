# Sample REST Service
In sample-server we have provided you with a very simple working web-service that has the same approach to this project (uses app/db). You should read through this *entire* code first and run a few simple examples.

### S1

First start the server in a one terminal (note the export command may not be needed)
```
cd server
export FLASK_APP=app.py
flask run
```

You should see something like
```
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
INFO:werkzeug: * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
that indicates the server is running on your localhost (127.0.0.1) and port 5000. 

### S2 
You can then check that you can connect to the server and receive a valid response.
We will first want to invoke the "homepage" that listens to the default URL for the server address (host and port). 
In app.py this maps to the following function which is mapped to the URI `/`
```
# hello world
@app.route('/')
def hello_world():
    data = {"message": "Hello, World!"}
    return jsonify(data)
```

You should then in another terminal or your favorite web browser test that you can connect to the server and receive the hello world JSON response. In your browser simply go to `http://127.0.0.1:5000/`. An alternative approach that you will want for testing is to you the command line tool `curl`, which is installed on many linux and mac platforms by default.
While the server is running in one terminal, open and another and run `curl http://127.0.0.1:5000/` which should give you the JSON hello world also.

### S3
Then visit the /create endpoint `curl http://127.0.0.1:5000/create` which will create the table for the simple app. Calling this endpoint more than once will work, and on any subsequent invocation, it will drop the existing table and recreate it, effectively "resetting" your database. Trace through the code and ensure you understand how the app.py, db.py, and create.sql work together. Your solution will involve the same process for setting up and resetting your database. **Note** that you would never have such an endpoint on a real service as your database would be ruined with one click, but for our testing this makes things easy.

### S4
Next, let's test the POST endpoint to add data. We have provided a simple shell script `add_test_rec.sh` that will invoke the endpoint http://127.0.0.1:5000/new with a JSON object as the request body/payload.
This script simply invokes
```
curl -v -X POST http://127.0.0.1:5000/new -iH 'Content-Type: application/json' -d '{"field1":"XYZ","field2":0}'
```

Look at the corresponding function mapped to `/new` in app.py and note the difference with `/create`, Try invoking the test script more than once and see how the code behaves. Try running create and re-running. See if you can create a new record with a new field1.

### S5 
Next examine the two GET endpoints to read data from the DB. `/test` returns a list of all records in the table. `/test/<id>` returns the details for one particular record in the DB. It tries to lookup in the table where field1=<id>. For example `curl http://127.0.0.1:5000/test/abcde` will look up the record where field1='abcde'. This endpoint also adds an array to the result that counts up from field2. This will be useful for your later code where you might not be able to get everyhing in one query. Take a look at these endpoints in app and db. Understand how they work!