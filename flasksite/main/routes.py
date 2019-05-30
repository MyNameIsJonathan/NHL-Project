import ast
import pandas as pd
from flask import render_template, Blueprint
import NHL_scrape_functions as nhl
import recurly
from flasksite.config import Config

# Create a blueprint for the Flask site
main = Blueprint('main', __name__)

# Establish recurly information
myConfig = Config()
recurly.SUBDOMAIN = myConfig.RECURLY_SUBDOMAIN
recurly.API_KEY = myConfig.RECURLY_API_KEY
recurly.DEFAULT_CURRENCY = 'USD'

# Instantiate the route decorators for Flask
@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/nhl_stats")
def nhl_stats():

    # Create engine connection to DB
    nhlengine = nhl.nonFlaskCreateEngine()

    # Select top scorers and return as DF
    mydf = pd.read_sql_query(("SELECT * FROM 2018_2019_stats ORDER BY G DESC, "
                              "A DESC LIMIT 10"), index_col='Player',
                             con=nhlengine)
    mydf = mydf.reindex((['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH',
                          'GW', 'S', 'Shifts', 'TOI']), axis=1)

    # Select top 10 lastTime and return as DF
    lastTime = pd.read_sql_query(("SELECT * FROM 2018_2019_LastTime WHERE (G > "
                                  "'2000-10-04') AND (Last_Game_Date > "
                                  "'2018-08-01') ORDER BY G ASC, A ASC "
                                  "LIMIT 10"),
                                 index_col='Player', con=nhlengine)
    lastTime = lastTime.reindex((['Last_Game_Date', 'G', 'A', 'PTS','PIM', 'EV',
                                  'Plus', 'Minus', 'PP', 'SH', 'GW', 'S']),
                                axis=1)
    for column in lastTime.columns:
        try:
            lastTime[column] = pd.to_datetime(lastTime[column])
        except ValueError:
            pass

    # Select top 10 gamesSince and return as DF
    gamesSince = pd.read_sql_query(("SELECT * FROM 2018_2019_GamesSince ORDER "
                                    "BY G DESC, A DESC LIMIT 10"),
                                   index_col='Player', con=nhlengine)
    gamesSince = gamesSince.reindex((['G', 'A', 'PTS', 'Plus', 'Minus', 'PIM',
                                      'EV', 'PP', 'SH', 'GW', 'S',
                                      'Total Recorded Games']), axis=1)

    # Convert DFs to html
    myDFHTML = mydf.head(10).to_html(classes=['table', 'stat-table'],
                                     index_names=False, justify='center')
    lastTimeHTML = lastTime.head(10).to_html(classes=['table', 'stat-table'],
                                             index_names=False,
                                             justify='center')
    gamesSinceHTML = gamesSince.head(10).to_html(
        classes=['table', 'stat-table'], index_names=False, justify='center')


    return render_template('nhl_stats.html', title='NHL Stats', myDF=myDFHTML,
                           lastTimeDF=lastTimeHTML, gamesSinceDF=gamesSinceHTML)

@main.route("/todays_players")
def todays_players():

    # Create engine
    nhlengine = nhl.nonFlaskCreateEngine()

    # Open dict of todays drought leaders and int of number of players today.
    today = pd.to_datetime('today').date()
    droughtsFound = False
    # Loop through days to find last available input in todaysDroughts
    while droughtsFound is False: # If yields no rows, find last available row
        todaysDroughts = nhlengine.execute("SELECT * FROM todaysDroughts WHERE Date = '%s' LIMIT 1" % (today))
        for row in todaysDroughts:
            droughtsFound = True
            droughtsDict = ast.literal_eval(row[2])
            numberOfPlayersToday = row[3]
            break
        today -= pd.Timedelta(days=1)

    return render_template('todays_players.html', title="Today's Players",
                           todaysDroughts=droughtsDict,
                           numberOfPlayersToday=numberOfPlayersToday)

@main.route("/stamkostweets")
def stamkostweets():

    # Create engine
    nhlengine = nhl.nonFlaskCreateEngine()

    #Open tweets mentioning stamkos from the last week
    myTweets = nhlengine.execute("SELECT * FROM stamkosTweets")

    my_tweets = {}

    for i, tweet in enumerate(myTweets):
        my_tweets[i] = {
            'created_at': pd.to_datetime(tweet[0]).strftime('%a %b %-d, %Y'),
            'text': tweet[1],
            'author': tweet[2]
        }

    return render_template('stamkostweets.html', title='Stamkos Tweets',
                           my_tweets=my_tweets, my_length=len(my_tweets))


@main.route("/create_recurly_account")
def create_recurly_account():
    return render_template('create_recurly_account.html')
