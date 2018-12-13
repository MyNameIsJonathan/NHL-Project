from flask import render_template, request, Blueprint
import pandas as pd
import NHL_scrape_functions
import datetime

# source /Users/jonathanolson/Projects/Environments/nhl_flask/bin/activate

main = Blueprint('main', __name__)


# These functions 'create' routes to pages within your site. 
# This one creates the 'home' page route, while the one 
# below creates the NHL Stats page route
@main.route("/")  #Having two @app. here means that this page is rendered when either website.com/ or website.com/home are visited
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/nhl_stats")
def nhl_stats():

    # Open dict of today's HTML files
    todaysHTML = NHL_scrape_functions.opentodaysHTML()

    return render_template('nhl_stats.html', title = 'NHL Stats', myDF=todaysHTML['myDF'], lastTimeDF=todaysHTML['lastTimeDF'], gamesSinceDF=todaysHTML['gamesSinceDF'])


@main.route("/todays_players")
def todays_players():
    # Open dict of todays drought leaders and int of number of players today
    todaysDroughts = NHL_scrape_functions.openTodaysDroughts()
    numberOfPlayersToday = NHL_scrape_functions.openNumberOfPlayers()

    return render_template('todays_players.html', title = "Today's Players", todaysDroughts=todaysDroughts, numberOfPlayersToday=numberOfPlayersToday)