# RHVis

A complete bugzilla visualization tool dedicated to work and visualize the Redhat Bugzilla data.

The application consists of the following functionality
- Data visualizations and aggregations
- Leaderboard
- Components visualizations

### Setup Developers (Linux / Mac)

1. `git clone https://github.com/sudheesh001/RHVis`
2. `cd RHVis`
3. `virtualenv venv`
4. `source venv/bin/activate`
5. `cp config.temp.py config.py`

Set up the config.py with the required MySQL `MYSQL_DATABASE_USER = username` and `MYSQL_DATABASE_PASSWORD = password`. 

Create a database on MySQL called `RHVis`

After doing all of the above steps successfully run the following commands

1. `pip install -r requirements.txt`
2. After successful installation of the requirements run `python server.py`

The server initially sets up all its required data sources and then is ready to serve them, It'll display a line saying
```
The server is now Online.
 You can access the server at localhost:8080
```

The server should now be running on `localhost:8080`

To deploy the application to a live server do the following changes in the last line of `server.py` running as screen service.


```python
app.run(host= '0.0.0.0', port=80)
```