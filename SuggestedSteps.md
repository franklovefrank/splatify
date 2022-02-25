# Suggested Steps
These are the suggested steps for completing this project. Note (2/21/22) we will add more tests by the end of the week for the remaining 

## Step 1 Configure DB
Look through the end point/API description in the link above and first design you ERD. Create your API using any tool you want (including paper and taking picture with your camera), but get your ERD diagram in the splatify/ folder and call it `splat2.{png|pdf|jpg}`.  You must use the notation we use in class. The exception to this is if you use [draw.io/](https://draw.io/).  The default ER-diagram is not our format, but you can change the edges and relationships to align with our style. Using their PK notation is fine, but remove FKs from entities. The updated ER-diagram should reflect how data enters the system (i.e. think about how songs are created).

After you create your ERD diagram add the tables in `server/schema/create.sql`. Each statement should be separated by a semicolon. 
In this file you should run `drop table [table_name] if exists;` I suggest dropping tables in the inverse order of how you create them to avoid issues with foreign keys (eg create table A then B, with B having a FK to A -- you should drop B then A). Please test that your create.sql file works. **If the /create end point does not work you will lose 35% on this submission.**  If you have sqlite3 as a program installed you can verify that the script runs by executing the following command from the server directory `sqlite3 splatDB.sqlite3 < schema/create.sql`. You can then connect to DB `sqlite3 splatDB.sqlite3` and then run `.schema`. If you do not have the ability or desire to install sqlite3, you can test by using the `/create` endpoint and issue later commands.


## Step 2: Save/Post Album
Complete the function
```
@app.route('/album', methods=["POST"])
def add_album():
```
This function will take a JSON as input (`request.json`) which is passed to the `add_album` function in the db class.  The data in this JSON will have details on the album, the artists, associated with the album, and the list of songs (in order) on the album. Note that each song will have 1 or more artists associated with it. A song can appear on more than one album, and artists may be associated with more than one album.

### Test 2.1 (first test of step 2)
You should be able to test this with from the data dir (assuming default host and port): 

```
curl -iH "Content-Type: application/json" --data @album.json http://localhost:5000/album
```

or  from the client dir:

```
python3 client.py -f data/album1-test.json
```

or via the web app http://127.0.0.1:5000/web/post_data

Your output will be empty, but you should see a response code of 201 (assuming you have not already inserted the album before).


### Test 2.2
In a new terminal, while the server is running, run from the client directory `python3 client.py -f data/album2-test.json`

This test will add two albums, where 1 artist overlaps.

### Test 2.3 
In a new terminal, while the server is running, run from the project directory root run the following scripts

```
python3 client/client.py -f data/album10-test.json
python3 client/client.py -f data/album50-test.json
python3 client/client.py -f data/albumfull-test.json
```

These tests add increasingly more albums. 



## Step 3: Read a song by ID
Implement the function
```
@app.route('/songs/<song_id>', methods=["GET"])
def find_song(song_id):
```
### Test 3.1
After running Test 2.1 or 2.2  test with
```
curl http://localhost:5000/songs/115
```
or go to http://localhost:5000/songs/115 in your favorite browser.


If you had a fresh (empty) DB before running 2.1 you should an output like
```
{"song_id":115,"song_name":"Reign Over Me","length":324,"artist_ids":[41],"album_ids":[76]}
```

### Test 3.2 
Coming this week for checking many songs.

## Step 4: 
Complete the remaining APIs. This includes the end points get for getting albums and getting artist details, along with the three analytic end points. The documentation linked shows expected output. 

We will provide additional tests by the end of the week.