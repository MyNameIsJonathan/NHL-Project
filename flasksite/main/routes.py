from flask import render_template, request, Blueprint, send_from_directory
import NHL_scrape_functions as nhl
import pandas as pd
import datetime
import random
import os

main = Blueprint('main', __name__)

# These functions 'create' routes to pages within your site. 
# This one creates the 'home' page route, while the one 
# below creates the NHL Stats page route
@main.route("/")  #Having two @main. here means that this page is rendered when either website.com/ or website.com/home are visited
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
    #Open tweets mentioning stamkos from the last week
    my_tweets = pd.read_pickle(f"pickleFiles/stamkosTweets/stamkosTweets_{pd.to_datetime('today').date()}.pickle")
    my_length = len(my_tweets)
    my_numbers = random.sample(range(my_length), my_length)
    my_tweets = [my_tweets[i] for i in my_numbers]

    return render_template('stamkostweets.html', title='Stamkos Tweets', my_tweets=my_tweets, my_length=my_length)

@main.route("/workflow")
def workflow():
    return render_template('workflow.html', title = 'NHL Stat Workflow')
