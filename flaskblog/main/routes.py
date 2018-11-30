from flask import render_template, request, Blueprint
from flaskblog.models import Post
import pandas as pd
import NHL_scrape_functions
import datetime

# source /Users/jonathanolson/Projects/Environments/nhl_flask/bin/activate

main = Blueprint('main', __name__)


#These functions 'create' pages within your site. 
# This one creates the 'home' page, while the one 
# below creates the NHL Stats page
@main.route("/")  #Having two @app. here means that this page is rendered when either website.com/ or website.com/home are visited
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/nhl_stats")
def nhl_stats():

    # Load in the three main dataframes and select for current players, if necessary
    myDF = NHL_scrape_functions.openLatestMyDF().sort_values('G', ascending=False)
    myDF['TOI'] = myDF['TOI'].astype(int)
    myDF = myDF.sort_values(['G', 'PTS'], ascending=False)
    myDF = myDF.reindex(['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Shifts', 'TOI'], axis=1)

    lastTimeDF = NHL_scrape_functions.openLatestLastTime()
    lastTimeDF = lastTimeDF[lastTimeDF['Last Game Date'] >= pd.to_datetime('2018-7-1', format="%Y-%m-%d").date()] # Select for player who've played in last 30 days only
    lastTimeDF = lastTimeDF[lastTimeDF['G'] > pd.to_datetime('2000-10-03', format="%Y-%m-%d").date()] # Players who've never scored have last goal set as 2000/10/3. Remove these palyers
    lastTimeDF = lastTimeDF.sort_values(['G', 'A'])
    lastTimeDF = lastTimeDF.reindex(['Last Game Date', 'G', 'A', 'PTS', '+', '-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S'], axis=1)

    # Grab the players in this df, for slicing retired players from the gamesSince DF
    currentPlayers = lastTimeDF.index

    gamesSinceDF = NHL_scrape_functions.openLatestGamesSince()
    gamesSinceDF = gamesSinceDF.loc[currentPlayers, :]
    gamesSinceDF = gamesSinceDF.sort_values(['G', 'A'], ascending=False)

    # Replace date '2000-10-3' with 'Never'
    myDF = myDF.replace(to_replace=pd.to_datetime('2000-10-3', format="%Y-%m-%d").date(), value='Never')
    lastTimeDF = lastTimeDF.replace(to_replace=pd.to_datetime('2000-10-3', format="%Y-%m-%d").date(), value='Never')
    gamesSinceDF = gamesSinceDF.replace(to_replace=pd.to_datetime('2000-10-3', format="%Y-%m-%d").date(), value='Never')

    # Convert DFs to html
    myDF=myDF.head(10).to_html(classes=['table', 'stat-table'], index_names=False, justify='center')
    lastTimeDF=lastTimeDF.head(10).to_html(classes=['table', 'stat-table'], index_names=False, table_id="lasttime-table", justify='center')
    gamesSinceDF=gamesSinceDF.head(10).to_html(classes=['table', 'stat-table'], index_names=False, justify='center')

    # Set pandas options
    pd.set_option('colheader_justify', 'center') 

    return render_template('nhl_stats.html', title = 'NHL Stats', myDF=myDF, lastTimeDF=lastTimeDF, gamesSinceDF=gamesSinceDF)


@main.route("/announcements")
def announcements():
    return render_template('announcements.html', title = 'Announcements')