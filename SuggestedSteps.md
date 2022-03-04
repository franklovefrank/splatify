# Suggested Steps
These are the suggested steps for completing this project. 

## Step 1 Configure DB
Look through the end point/API description in the link above and first design you ERD. Create your API using any tool you want (including paper and taking picture with your camera), but get your ERD diagram in the splatify/ folder and call it `splat2.{png|pdf|jpg}`.  You must use the notation we use in class. The exception to this is if you use [draw.io/](https://draw.io/).  The default ER-diagram is not our format, but you can change the edges and relationships to align with our style. Using their PK notation is fine, but remove FKs from entities. The updated ER-diagram should reflect how data enters the system (i.e. think about how songs are created).

After you create your ERD diagram add the tables in `server/schema/create.sql`. Each statement should be separated by a semicolon. 
In this file you should run `drop table [table_name] if exists;` I suggest dropping tables in the inverse order of how you create them to avoid issues with foreign keys (eg create table A then B, with B having a FK to A -- you should drop B then A). Please test that your create.sql file works. **If the /create end point does not work you will lose 35% on this submission.**  If you have sqlite3 as a program installed you can verify that the script runs by executing the following command from the server directory `sqlite3 splatDB.sqlite3 < schema/create.sql`. You can then connect to DB `sqlite3 splatDB.sqlite3` and then run `.schema`. If you do not have the ability or desire to install sqlite3, you can test by using the `/create` endpoint and issue later commands.

Note if your create.sql file is missing simply run
```
cd server
mkdir schema
touch schema/create.sql
git add schema/create.sql
```

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
In a new terminal, while the server is running, run from the client directory `python3 client.py -f ../data/album2-test.json`

This test will add two albums, where 1 artist overlaps.

### Test 2.3 
In a new terminal, while the server is running, run from the project *directory root* run the following scripts

```
python3 client/client.py -f data/10album/album10-test.json
python3 client/client.py -f data/50album/album50-test.json
python3 client/client.py -f data/full/albumfull-test.json
```

These tests add increasingly more albums. Once you feel these are working, try the test which has a bad album at the end, which has a song with no artists. You should verify that the album_id 999 is not present in your database after this run, and that other album_ids are (such as 5). You should also not see new songs/artists from the bad album, such as artist_id 45.

```
python3 client/client.py -f data/10album/album10-2.3.json
```



## Step 3: Read a song by ID
[Implement the function get song](http://people.cs.uchicago.edu/~aelmore/class/db/splatify.html#tag/All/paths/~1songs~1{song_id}/get)
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
You should now be able to run the following test assuming all your prior tests work

```
python3 client/client.py -f data/10album/album10-3.2.json
```

And also the full test, the remaining tests will use the full dataset:

```
python3 client/client.py -f data/full/full-3.2.json
```



## Step 4: 
Complete the remaining APIs. This includes the end points get for getting albums and getting artist details, along with the three analytic end points. The documentation linked shows expected output.  These tests run multiple checks, so you may want to duplicate and modify a test, or inspect an endpoint by hand first.

The tests below for the 'full data set' will allow you test each endpoint.

[Song by album](http://people.cs.uchicago.edu/~aelmore/class/db/splatify.html#tag/All/paths/~1songs~1by_album~1{album_id}/get):
```
python3 client/client.py -f data/full/full-4.1.json
```

[Songs by artist](http://people.cs.uchicago.edu/~aelmore/class/db/splatify.html#tag/All/paths/~1songs~1by_artist~1{artist_id}/get):
```
python3 client/client.py -f data/full/full-4.2.json
```

[Get album](http://people.cs.uchicago.edu/~aelmore/class/db/splatify.html#tag/All/paths/~1albums~1{album_id}/get):
```
python3 client/client.py -f data/full/full-4.3.json
```

[Avg length of song by artist](http://people.cs.uchicago.edu/~aelmore/class/db/splatify.html#tag/All/paths/~1analytics~1artists~1avg_song_length~1{artist_id}/get) (don't forget round to 1 decimal using round(x,1) where x is the field in the query):

```
python3 client/client.py -f data/full/full-4.4.json
```

**If you are a graduating senior**  throw your hands up and call it a day! (well commit, push, and submit and then do so). You are done. Otherwise continue...


[Get albums by artist](http://people.cs.uchicago.edu/~aelmore/class/db/splatify.html#tag/NonGrad/paths/~1albums~1by_artist~1{artist_id}/get):
```
python3 client/client.py -f data/full/full-4.5.json
```

[Get artist](http://people.cs.uchicago.edu/~aelmore/class/db/splatify.html#tag/NonGrad/paths/~1artists~1{artist_id}/get):
```
python3 client/client.py -f data/full/full-4.6.json
```

[Get artists with longest sum of songs](http://people.cs.uchicago.edu/~aelmore/class/db/splatify.html#tag/NonGrad/paths/~1analytics~1artists~1top_length~1{num_artists}/get):
```
python3 client/client.py -f data/full/album-full.json
```

**YOU DID IT!** commit, push, and submit!
