from flask import render_template, request, Blueprint, send_from_directory
from flasksite import mysql
import NHL_scrape_functions as nhl
import tweepyrun as twp
import pandas as pd
import datetime
import random
import os
import ast
import json


# Create a blueprint for the Flask site
main = Blueprint('main', __name__)

# Instantiate the route decorators for Flask
@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/nhl_stats")
def nhl_stats():

    # Create engine connection to DB
    engine = nhl.nonFlaskCreateEngine()

    # Select top scorers and return as DF
    mydf = pd.read_sql_query(("SELECT * FROM 2018_2019_stats ORDER BY G DESC, "
    "A DESC LIMIT 10"), index_col='Player', con=engine)
    mydf = mydf.reindex((['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH',
    'GW', 'S', 'Shifts', 'TOI']), axis=1)

    # Select top 10 lastTime and return as DF
    lastTime = pd.read_sql_query(("SELECT * FROM 2018_2019_LastTime WHERE (G > '2000-10-04') AND (Last_Game_Date > '2018-08-01') ORDER BY G ASC, A ASC LIMIT 10"), index_col='Player', con=engine)
    lastTime = lastTime.reindex((['Last_Game_Date', 'G', 'A', 'PTS', '+/-',
    'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Shifts', 'TOI']), axis=1)
    for column in lastTime.columns:
        try:
            lastTime[column] = pd.to_datetime(lastTime[column])
        except ValueError:
            pass

    # Select top 10 gamesSince and return as DF
    gamesSince = pd.read_sql_query(("SELECT * FROM 2018_2019_GamesSince ORDER "
    "BY G DESC, A DESC LIMIT 10"), index_col='Player', con=engine)
    gamesSince = gamesSince.reindex((['G', 'A', 'PTS', 'Plus', 'Minus', 'PIM',
    'EV', 'PP', 'SH', 'GW', 'S', 'Total Recorded Games']), axis=1)

    # Create the link to the database
    # cursor = mysql.get_db().cursor()

    # Execute query for mydf
    # cursor.execute("SELECT * FROM 2018_2019_stats ORDER BY G DESC LIMIT 10")
    # mydf = cursor.fetchall()
    # mydf = pd.DataFrame(mydf)

    # Execute query for lastTime
    # cursor.execute("SELECT * FROM 2018_2019_LastTime ORDER BY G DESC LIMIT 10")
    # lastTime = cursor.fetchall()

    # Execute query for gamesSince
    # cursor.execute("SELECT * FROM 2018_2019_GamesSince ORDER BY G DESC LIMIT 10")
    # gamesSince = cursor.fetchall()

    # Select each component from myHTML (index: value --> 0: id, 1: date, 2:
    #mydf, 3: lastTime, 4: gamesSince). Convert these dicts to DataFrames
    # for item in myHTML:
    #     mydf = pd.DataFrame.from_dict(json.loads(item[2])).sort_values(['G', 'A'], ascending=False) #mydf is stored in column #2
    #     lastTime = pd.DataFrame.from_dict(json.loads(item[3])) # lastTime is stored in column #3
    #     gamesSince = pd.DataFrame.from_dict(json.loads(item[4])) # gamesSince is stored in column #4

    # Convert DFs to html
    myDFHTML = mydf.head(10).to_html(classes=['table', 'stat-table'], index_names=False, justify='center')
    lastTimeHTML = lastTime.head(10).to_html(classes=['table', 'stat-table'], index_names=False, justify='center')
    gamesSinceHTML = gamesSince.head(10).to_html(classes=['table', 'stat-table'], index_names=False, justify='center')

    return render_template('nhl_stats.html', title = 'NHL Stats', myDF=myDFHTML, lastTimeDF=lastTimeHTML, gamesSinceDF=gamesSinceHTML)

@main.route("/todays_players")
def todays_players():

    # Open dict of todays drought leaders and int of number of players today
    today = pd.to_datetime('today').date()
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT * FROM todaysDroughts WHERE Date = '%s'" % (today))
    todaysDroughts = cursor.fetchone()

    # Row proxy is indexable; select the dictionary and number of players today
    droughtsDict = ast.literal_eval(todaysDroughts[2])
    numberOfPlayersToday = todaysDroughts[3]

    return render_template('todays_players.html', title = "Today's Players", todaysDroughts=droughtsDict, numberOfPlayersToday=numberOfPlayersToday)

@main.route("/stamkostweets")
def stamkostweets():

    cursor = mysql.get_db().cursor()

    #Open tweets mentioning stamkos from the last week
    cursor.execute("SELECT * FROM stamkosTweets")
    cursorTweets = cursor.fetchall()

    my_tweets = {}

    for i, tweet in enumerate(cursorTweets):
        my_tweets[i] = {
            'created_at': pd.to_datetime(tweet[0]).strftime('%a %b %-d, %Y'),
            'text': tweet[1],
            'author': tweet[2]
        }

    return render_template('stamkostweets.html', title='Stamkos Tweets', my_tweets=my_tweets, my_length=len(my_tweets))
