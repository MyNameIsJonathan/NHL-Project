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

    # THIS IS OPENTODAYSHTML

    # Open dict of today's HTML files
    cursor = mysql.get_db().cursor()

    # Get the last row of the table, sorted by date. This means itll be today's html, unless there was an error, allowing it to fall back on yesterdays html
    cursor.execute("SELECT * FROM dailyDataFrames ORDER BY date DESC LIMIT 1")
    myHTML = cursor.fetchall()

    # Select each component from myHTML (index: value --> 0: id, 1: date, 2: mydf, 3: lastTime, 4: gamesSince). Convert these dicts to DataFrames
    for item in myHTML:
        mydf = pd.DataFrame.from_dict(json.loads(item[2]))
        lastTime = pd.DataFrame.from_dict(json.loads(item[3]))
        gamesSince = pd.DataFrame.from_dict(json.loads(item[4]))

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
    todaysDroughts = cursor.fetchone()[0]

    droughtsDict = ast.literal_eval(todaysDroughts[2])
    numberOfPlayersToday = todaysDroughts[-1]

    return render_template('todays_players.html', title = "Today's Players", todaysDroughts=droughtsDict, numberOfPlayersToday=numberOfPlayersToday)

@main.route("/stamkostweets")
def stamkostweets():

    cursor = mysql.get_db().cursor()

    # cursor = mysql.get_db().cursor()

    #Open tweets mentioning stamkos from the last week
    cursor.execute("SELECT * FROM stamkosTweets")
    my_tweets = cursor.fetchone()[0]

    # Choose a random order of tweets
    # my_numbers = random.sample(range(len(my_tweets)), len(my_tweets))
    # my_tweets = [my_tweets[i] for i in my_numbers]

    return render_template('stamkostweets.html', title='Stamkos Tweets', my_tweets=my_tweets, my_length=len(my_tweets))

@main.route("/workflow")
def workflow():
    return render_template('workflow.html', title = 'NHL Stat Workflow')
