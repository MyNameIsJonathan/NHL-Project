from flask import render_template, request, Blueprint, send_from_directory
from flask_mysqldb import MySQL
import NHL_scrape_functions as nhl
import tweepyrun as twp
import pandas as pd
import datetime
import random
import os

# Create a blueprint for the Flask site
main = Blueprint('main', __name__)
mysql = MySQL(main)

# Instantiate the route decorators for Flask
@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/nhl_stats")
def nhl_stats():

    # Open dict of today's HTML files
    todaysHTML = nhl.opentodaysHTML()

    return render_template('nhl_stats.html', title = 'NHL Stats', myDF=todaysHTML['myDF'], lastTimeDF=todaysHTML['lastTimeDF'], gamesSinceDF=todaysHTML['gamesSinceDF'])

@main.route("/todays_players")
def todays_players():
    # Open dict of todays drought leaders and int of number of players today
    todaysDroughts = nhl.openTodaysDroughts()
    numberOfPlayersToday = nhl.openNumberOfPlayers()

    return render_template('todays_players.html', title = "Today's Players", todaysDroughts=todaysDroughts, numberOfPlayersToday=numberOfPlayersToday)

@main.route("/stamkostweets")
def stamkostweets():

    # Create an engine SQLAlchemy connection to the stamkosTweets table in MySQL DB
    engine = nhl.openNHLMySQL('stamkosTweets')

    #Open tweets mentioning stamkos from the last week
    my_tweets = twp.openTweets(engine)

    # Choose a random order of tweets
    # my_numbers = random.sample(range(len(my_tweets)), len(my_tweets))
    # my_tweets = [my_tweets[i] for i in my_numbers]

    return render_template('stamkostweets.html', title='Stamkos Tweets', my_tweets=my_tweets, my_length=len(my_tweets))

@main.route("/workflow")
def workflow():
    return render_template('workflow.html', title = 'NHL Stat Workflow')
