"""

This module contains all of the functions to scrape data from the web, clean
that data, and incorporate it into the various MySQL databases for display on
my website at https://jonathanolson.us

"""


import datetime
import time
import json
import logging
import requests
import pandas as pd
import backupMaintainer as backups
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from flasksite.config import Config


# Configure the logger
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# Format the messages logged
# formatter = logging.Formatter('%(lebelname)s:%(name):3%message)s')

# Specify the file to which we'll log
# file_handler = logging.fileHandler('NHL_Scrape.log')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

'--------------- MySql Functions ---------------'


def non_flask_create_engine():
    """
    Opens a connection to the provided table in the NHL Stats MySQL Database.

    Args:
        None

    Returns:
        sqlalchemy.engine.base.Engine - A connection to the NHL MySQL Database
                                        for the given table

    Raises:
        None
    """

    myConfig = Config()

    MYSQL_DATABASE = myConfig.MYSQL_DATABASE_DB
    MYSQL_PASSWORD = myConfig.MYSQL_DATABASE_PASSWORD
    MYSQL_PORT = myConfig.MYSQL_DATABASE_PORT
    MYSQL_HOST = myConfig.MYSQL_DATABASE_HOST
    MYSQL_USER = myConfig.MYSQL_DATABASE_USER

    myURL = (f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}')

    engine = create_engine(myURL)

    print('MySQL Connection Engine successfully created')

    return engine


def get_first_unscraped_day(engine):
    """
    Uses the 'games' MySQL table to find the latest day whose games are
    not yet scraped

    Args:
    engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                            NHL_Database MySQL database

    Returns:
    datetime.date - Date of latest day whose games are not
                    yet scraped

    Raises:
    None
    """

    games = openMySQLTable('games', engine, myIndex=None)
    unscraped_days = games.loc[games['Game'].isnull()]
    first_unscraped_day = unscraped_days.loc[:, 'Date'].min().date()

    return first_unscraped_day


def openMySQLTable(table_name, engine, myIndex='Player'):
    """
    Opens MySQL table, using provided SQLAlchemy engine. Formats output based
    on which table is specified

    Args:
    table_name: String - Name of table to return
    engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                            NHL_Database MySQL database
    myIndex: String - Specifies index to set in returned pandas dataframe

    Returns:
    A Pandas DataFrame of the specified table, with the index set to 'Player'

    Raises:
    None
    """

    myRegularTables = (['2018_2019_GamesSince', '2018_2019_stats',
                        'gamesBackup', 'gamesSinceBackup', 'lastTimeBackup',
                        'statsBackup', 'todaysDroughts', 'dailyDataFrames',
                        'stamkosTweets'])

    if table_name == 'games':
        return pd.read_sql_table('games', engine, parse_dates=['Date'])
    elif table_name == '2018_2019_LastTime':
        if myIndex is None:
            return pd.read_sql_table('2018_2019_LastTime', engine, parse_dates=(
                ['G', 'A', 'PTS', 'Plus', 'Minus', 'PIM', 'EV', 'PP', 'SH',
                 'GW', 'S', 'Last_Game_Date', 'Last_Game_Date']))
        else:
            return pd.read_sql_table('2018_2019_LastTime', engine, parse_dates=(
                ['G', 'A', 'PTS', 'Plus', 'Minus', 'PIM', 'EV', 'PP', 'SH',
                 'GW', 'S', 'Last_Game_Date', 'Last_Game_Date']))\
                .set_index(myIndex)
    elif table_name in myRegularTables:
        if myIndex is None:
            return pd.read_sql_table(table_name, engine)
        return pd.read_sql_table(table_name, engine).set_index(myIndex)


def save_mysql_table(myDF, dbName, engine, reset_index=True):
    """
    Saves MySQL table after resetting index, if necessary. This prevents losing
    the index in event of loading the table without specifying the index,
    thereby losing the index.

    Args:
    myDF: Pandas DataFrame - A dataframe to save
    dbName: String - Name of the dataframe. Almost always "NHL_Database"
    engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                            NHL_Database MySQL database
    reset_index: Boolean - Instructs save method to reset/not reset index.
                           Resetting index returns sequential list [0, 1, 2...]
                           to index and returns column of player names to
                           normal column.

    Returns:
    None

    Raises:
    None
    """

    if reset_index is True:
        myDF = myDF.reset_index()
    myDF.to_sql(
        name=dbName,
        con=engine,
        index=False,
        if_exists='replace')

def backupTables(engine):

    """
    Saves the current MySQL NHL_Database tables as pickled pandas DFs. Looks
    for Pickle files labeled with todays date. Upon finding none, saves
    dataframes as pickle files labeled with today's date.

    Args:
    engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                            NHL_Database MySQL database

    Returns:
    None

    Raises:
    None
    """

    today = pd.to_datetime('today').date()

    try:
        pd.read_pickle(f'/NHL-Project/mysqlbackups/gs_{today}')
    except FileNotFoundError:
        pass

    except FileNotFoundError:
        gs = openMySQLTable('2018_2019_GamesSince', engine, myIndex='Player')
        lt = openMySQLTable('2018_2019_LastTime', engine, myIndex='Player')
        stats = openMySQLTable('2018_2019_stats', engine, myIndex='Player')
        games = openMySQLTable('games', engine, myIndex=None)

        gs.to_pickle(f'/NHL-Project/mysqlbackups/gs_{today}')
        lt.to_pickle(f'/NHL-Project/mysqlbackups/lt_{today}')
        stats.to_pickle(f'/NHL-Project/mysqlbackups/stats_{today}')
        games.to_pickle(f'/NHL-Project/mysqlbackups/games_{today}')

'--------------- Single-Game-Specific Functions ---------------'

def getURLS(date):

    """
    Uses the given date to create the html links to www.hockey-reference.com
    for that day's games. Scrapes that website and creates the link for each of
    the games on that day

    Args:
    date: datetime.date - A specific date

    Returns:
    Tuple: Tuple - A tuple of lists

        [list] -- [boxscore_links : html links to the boxscores for each game
                   of each day]
        [list] -- [my_home_teams : list of home teams. The ith game's home
                   team is in the ith position in this list]
        [list] -- [my_away_teams : list of away teams. The ith game's away
                   team is in the ith position in this list]
        [list] -- [my_game_dates : dates for each game. ith game is in ith
                   position in this list]
    Raises:
    KeyError: Raises an exception.
    """

    print(f'Getting URLs for date: {date}')

    # Create the hockey-reference link for the day's games
    url = ('https://www.hockey-reference.com/boxscores/index.fcgi?'
           f'month={date.month}&day={date.day}&year={date.year}')

    # Record team names for each game
    my_days_games = pd.read_html(url)
    my_home_teams = []
    my_away_teams = []
    my_date = str(date.year) + '/' + str(date.month) + '/' + str(date.day)
    my_game_dates = []

    # Iterate through returned list of dfs, to record home and away team names
    for i in range(0, len(my_days_games)-2, 2):
        my_home_teams.append(my_days_games[i].iloc[1, 0])
        my_away_teams.append(my_days_games[i].iloc[0, 0])
        my_game_dates.append(my_date)

    # Retrieve links for following
    r = requests.get(url)
    html_content = r.text
    soup = BeautifulSoup(html_content, 'lxml')

    # Create a list of all links on the day's page
    links = soup.find_all('a')
    links = [a.get('href') for a in soup.find_all('a', href=True)]

    # Select for only boxscore links
    boxscore_links = []
    for link in links:
        if link[:10] == '/boxscores':
            boxscore_links.append('www.hockey-reference.com' + link)
    boxscore_links = boxscore_links[5:-7]
    boxscore_links = ['https://' + link for link in boxscore_links]

    return (boxscore_links, my_home_teams, my_away_teams, my_game_dates)

def scrapeGame(my_url, game_date, home_team_name, away_team_name):

    """
    Pulls stats from a single game, given the url (attained through getURLS)
    the date (also from getURLS), home and away teams

    Args:
    my_url: String - URl for the specific game (identified by home team and date)
    game_date: String - Date of the game
    home_team_name: String - Name of the home team
    away_team_name: String - Name of the away team

    Returns:
    df: pandas.DataFrame - a data-cleaned dataframe that has the game's stats

    Raises:
    None

    """

    # Read table from hockey-reference
    df_list = pd.read_html(my_url, header=1)

    # Select only teams' stats DataFrames, as the penalty dataframe will not
    # exist if there are no penalties, causing indexing issues otherwise
    myDFs = []
    for df in df_list:
        if 'G' in df.columns:
            myDFs.append(df)
    df_away = myDFs[0].iloc[:-1, 1:18]
    df_home = myDFs[1].iloc[:-1, 1:18]

    # Make 'Team' column
    df_away['Team'] = away_team_name
    df_home['Team'] = home_team_name

    # Combine the two teams' dataframes
    df = pd.concat([df_away, df_home], sort=True)

    # Make a 'Date' column, which will eventually be used to represent the last
    # time each player scored a goal
    df['Date'] = game_date
    df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d')
    df['Date'] = df['Date'].dt.date

    # Set player name to index
    df = df.set_index('Player')

    return df

def cleanGame(game_df):

    """
    Cleans individual game data. Drops superfluous columns, renames columns,
    round floats, etc.

    Args:
    game_df: pandas.DataFrame - The Pandas DataFrame of game data that needs
                                to be cleaned

    Returns:
    game_df: pandas.DataFrame - The same DataFrame, cleaned.

    Raises:
    None
    """

    # Delete columns that are only present in the datasets starting in 2014-2015
    cols_to_drop = (['EV.1', 'PP.1', 'SH.1', 'S%', 'EV.2', 'PP.2', 'SH.2',
                     'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17'])
    game_df = game_df.drop([column for column in cols_to_drop if column in game_df.columns], axis=1)

    # Rename columns for better readability
    game_df = game_df.rename(columns = {'SHFT':'Shifts'})

    #Fill NaN values to convert to int
    game_df = game_df.fillna(0)

    #Get int of minutes on ice from string "mm:ss"
    game_df['TOI'] = game_df['TOI'].str.split(':')
    game_df['TOI'] = game_df['TOI'].apply(lambda x: int(x[0]) + int(x[1])/60)
    game_df['TOI'] = game_df['TOI'].round(2)

    #Convert date column to string
    game_df['Date'] = pd.to_datetime(game_df['Date'], format='%Y-%m-%d')
    game_df['Date'] = game_df['Date'].astype(str)

    return game_df

'--------------- Todays Games Functions ---------------'

def findTodaysGames(engine):

    """
    Get today's date and create url, date string, and scrape data

    Args:
    engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                            NHL_Database MySQL database

    Returns:
    games: pandas.DataFrame - A slice of the 'games' DataFrame, where the 'Date'
    column is today's date

    Raises:
    None
    """

    today = pd.to_datetime('today').date()

    games = openMySQLTable('games', engine, myIndex=None)

    return games[games['Date'] == str(today)]

def todaysPlayerDroughts(todaysGames, engine):

    """
    Get stats for players who play today. Saves this information in the MySQL
    table 'todaysDroughts' as a single column

    Args:
    todaysGames: Type - This is the first param.
    engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                            NHL_Database MySQL database

    Returns:
    None

    Raises:
    None
    """

    #Get the list of teams playing today
    teams_playing_today = list(todaysGames['Home'].unique()) + list(todaysGames['Away'].unique())

    # Fill players_playing_today by iterating through the team-player dictionary
    # from the file team_creation.py
    NHL_teams_and_players = pd.read_pickle(
        ('/NHL-Project/pickleFiles/Teams/'
         'NHL_teams_and_players.pickle'))

    # Instantiate a list of player names who play today and fill it
    players_playing_today = []
    for team in teams_playing_today:
        players_playing_today.extend(
            [player.Name for player in NHL_teams_and_players[team]])
    players_playing_today = pd.Series(players_playing_today).unique()

    # Save how many players are playing today
    numberOfPlayersToday = len(players_playing_today)

    # Open yesterday's GamesSince df to see the games since each of today's players scored, etc.
    GamesSince = openMySQLTable('2018_2019_GamesSince', engine, myIndex='Player')
    todays_GamesSince = GamesSince.loc[players_playing_today, :]

    # Open yesterday's lastTimeDF
    lastTime = openMySQLTable('2018_2019_LastTime', engine, myIndex='Player')
    todays_lastTime = lastTime.loc[players_playing_today, :]

    # Save the top 5 players for each category of GamesSince, such as the 5
    # players who haven't scored in the most games
    todaysDroughts = {}

    #Select all columns except Total Recorded Games
    myColumns = ['G', 'A', 'PTS', 'Plus', 'Minus', 'PIM', 'EV', 'PP', 'SH',
                 'GW', 'S']

    # Loop through columns to select oldest feat for each. Skip player if
    # they've never accomplished selected feat within
    # the dates of my dataset (my dataset spans 2000-10-4 and later, so
    # date='2000-10-3')
    null_date = pd.to_datetime('2000-10-3', format="%Y-%m-%d").date()
    for column in myColumns:
        myAvailablePlayers = todays_lastTime.loc[todays_lastTime[column].dt.date > null_date].index
        mySlice = todays_GamesSince.loc[myAvailablePlayers, :]
        myPlayer = mySlice.loc[mySlice[column] == mySlice[column].max()].index[0]
        myDate = todays_lastTime.loc[myPlayer, column].date().strftime('%a %b %-d, %Y')

        todaysDroughts[column] = [myPlayer,
                                  int(todays_GamesSince.loc[myPlayer, column]),
                                  str(myDate)]

    # Append the new data to the todaysDroughts dataframe
    droughtsDF = openMySQLTable('todaysDroughts', engine, myIndex=None)
    newRow = pd.Series({
        'id': droughtsDF['id'].max() + 1,
        'Date': pd.to_datetime('today').date(),
        'todaysDroughts': todaysDroughts,
        'numberOfPlayersToday': numberOfPlayersToday})
    droughtsDF = droughtsDF.append(newRow, ignore_index=True)

    # Save droughtsDF as 'todaysDroughts'. No need to reset index as the columns
    # are : 'id', 'Date', 'todaysDroughts', 'numberOfPlayersToday'
    save_mysql_table(droughtsDF, 'todaysDroughts', engine, reset_index=False)

def makeTodaysHTML(engine):

    """
    Make the HTML tables from the pandas Dataframes (originally MySQL table
    entries) to be displayed on the website. Saves this information in the MySQL
    table 'dailyDataFrames' as a new row

    Args:
    engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                            NHL_Database MySQL database

    Returns:
    None

    Raises:
    None
    """

    # Load in the three main dataframes and select for current players, if necessary
    stats = openMySQLTable('2018_2019_stats', engine, myIndex='Player')
    lastTime = openMySQLTable('2018_2019_LastTime', engine, myIndex='Player')
    gamesSince = openMySQLTable('2018_2019_GamesSince', engine, myIndex='Player')

    # Clean myDF
    stats['TOI'] = stats['TOI'].astype(int)
    stats = stats.sort_values(['G', 'PTS'], ascending=False)
    stats = stats.reindex((['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH',
                            'GW', 'S', 'Shifts', 'TOI']), axis=1)

    # Clean lastTime
    # Select for players who've played in last 30 days only
    lastTime = lastTime[lastTime['Last_Game_Date'].dt.date >= \
        pd.to_datetime('2018-7-1', format="%Y-%m-%d").date()]
    # Players who've never scored have last goal set as 2000/10/3. Remove these players
    lastTime = lastTime[lastTime['G'].dt.date > \
        pd.to_datetime('2000-10-03', format="%Y-%m-%d").date()]
    lastTime = lastTime.sort_values(['G', 'A'])
    lastTime = lastTime.reindex(['Last_Game_Date', 'G', 'A', 'PTS', 'Plus',
                                 'Minus', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S'],
                                axis=1)

    # Grab the players in this df, for slicing retired players from the gamesSince DF
    currentPlayers = lastTime.index
    gamesSince = gamesSince.reindex(currentPlayers)
    gamesSince = gamesSince.sort_values(['G', 'A'], ascending=False)

    # Replace date '2000-10-3' with 'Never'
    stats = stats.replace(
        to_replace=pd.to_datetime('2000-10-3', format="%Y-%m-%d").date(),
        value='Never')
    lastTime = lastTime.replace(
        to_replace=pd.to_datetime('2000-10-3', format="%Y-%m-%d").date(),
        value='Never')
    gamesSince = gamesSince.replace(
        to_replace=pd.to_datetime('2000-10-3', format="%Y-%m-%d").date(),
        value='Never')

    # Set pandas options
    pd.set_option('colheader_justify', 'center')

    # Save the HTML strings in a dictionary, to be loaded on routes.py file for
    # display. This prevents it from being calculated everytime the user is
    # routed to "Today's Players"
    statsJSON = stats.iloc[:10, :].to_json()
    lastTimeJSON = lastTime.iloc[:10, :].to_json()
    gamesSinceJSON = gamesSince.iloc[:10, :].to_json()

    # Save JSONs of the three dataframes in the MySQL DB table = dailyDataFrames;
    dailyDataFrames = openMySQLTable('dailyDataFrames', engine, myIndex=None)
    newRow = pd.Series({
        'id': len(dailyDataFrames) + 1,
        'date': pd.to_datetime('today').date(),
        'stats': statsJSON,
        'lastTime': lastTimeJSON,
        'gamesSince': gamesSinceJSON})
    dailyDataFrames = dailyDataFrames.append(newRow, ignore_index=True)

    # Save the DF to the MySQL database
    save_mysql_table(dailyDataFrames, 'dailyDataFrames', engine, reset_index=False)

def opentodaysHTML(engine):

    """
     Retrieve the HTML for the Pandas DataFrames made using the function
     makeTodaysHTML(). Retrieves the top ten rows of the three DataFrames:
     1 - myDFHTML - Cumulative NHL stats
     2 - lastTimeHTML - Date of last accomplishment DataFrame
     3 - gamesSinceHTML - Number of games since DataFrame

    Args:
    engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                            NHL_Database MySQL database

     Returns:
     todaysHTML: Dict - A dictionary of the three aforementioned DataFrames as
                        HTML

     Raises:
     None
     """

    # Get the last row of the table, sorted by date. This means itll be today's
    # html, unless there was an error, allowing it to fall back on yest. html
    myHTML = engine.execute(
        f"SELECT * FROM dailyDataFrames ORDER BY date DESC LIMIT 1").fetchone()

    # Select each component from myHTML (index: value --> 0: id, 1: date,
    # 2: mydf, 3: lastTime, 4: gamesSince). Convert these dicts to DataFrames
    mydf = pd.DataFrame.from_dict(json.loads(myHTML['stats']))
    lastTime = pd.DataFrame.from_dict(json.loads(myHTML['lastTime']))
    gamesSince = pd.DataFrame.from_dict(json.loads(myHTML['gamesSince']))

    # Convert DFs to html
    myDFHTML = mydf.head(10).to_html(
        classes=['table', 'stat-table'],
        index_names=False,
        justify='center')
    lastTimeHTML = lastTime.head(10).to_html(
        classes=['table', 'stat-table'],
        index_names=False,
        justify='center')
    gamesSinceHTML = gamesSince.head(10).to_html(
        classes=['table', 'stat-table'],
        index_names=False,
        justify='center')

    todaysHTML = {
        'myDF': myDFHTML,
        'lastTime': lastTimeHTML,
        'gamesSince': gamesSinceHTML}

    return todaysHTML

def openTodaysDroughts(engine):

    """
    Retrieves a single row from the MySQL table 'todaysDroughts', where the date
    equals today's date.

    Args:
    engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                            NHL_Database MySQL database

     Returns:
     todaysDroughts - SQLAlchemy engine row proxy

     Raises:
     None
     """

    print('Opening todaysDroughts DF')

    today = pd.to_datetime('today').date()

    todaysDroughts = engine.execute(
        f"SELECT * FROM todaysDroughts WHERE Date = '{today}'").fetchone()

    print('todaysDroughts DF opened successfully')

    return todaysDroughts

'--------------- Single-Day Scrape Functions ---------------'

def scrapeSpecificDay(date, engine):

    """
    Scrape, clean, incorporate specific day's stats. This is a

    Args:
    date: datetime.date
    engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                            NHL_Database MySQL database

    Returns:
    None

    Raises:
    None
    """

    # Scrape URLs for the given date
    myGames = scrapeSpecificDaysURLS(engine, date)
    # Scrape the games from those URLs
    rawGames = scrapeSpecificDaysGames(myGames)
    # Clean the games' DFs
    cleanSpecificDaysGames(date, rawGames, engine)
    # Update the lastTime, gamesSince, and Overall Statistics tables in MySQL
    updateSpecificDaysLastTime(date, engine)
    updateSpecificGamesSince(date, engine)
    incorporateSpecificDaysStats(date, engine)

def scrapeSpecificDaysURLS(engine, date):

    """
    Scrapes all html links for the given date

    Args:
        date: datetime.date
        engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                                NHL_Database MySQL database

    Returns:
        daysGames: pandas.DataFrame - A Pandas DataFrame where
                                      the 'Date' column equals today's date

    Raises:
        None
    """

    daysGames = pd.read_sql_query(
        f"SELECT * FROM games WHERE Date = '{date}'", con=engine)

    daysGames['Game Number'] = daysGames['Game Number'].astype(int)

    if len(daysGames) == 0:
        return 'No Games Found'
    return daysGames

def scrapeSpecificDaysGames(myGames):

    """
     Takes pandas series of URLs to scrape game data from hockeyreference.com

     Args:
        myGames: pandas.DataFrame - A Pandas DataFrame where
                                    the 'Date' column equals today's date

     Returns:
     	rawGames: dictionary - A dictionary linking games to their Dataframes
            keys = home team name (string)
            values = game dataframe returned from function scrapeGame

     Raises:
     	None
     """

    #Create rawGames dict to store scraped games
    rawGames = {}

    number_of_games = len(myGames)
    print('Number of games to scrape = {}'.format(number_of_games))

    #Instantiate counter for reporting scrape progress and create % thresholds
    my_count = 0
    threshold_25 = int(number_of_games*0.25)
    threshold_50 = int(number_of_games*0.5)
    threshold_75 = int(number_of_games*0.75)

    # Use  html links to create games' dataframes
    for i in range(number_of_games):
        homeTeam = myGames.loc[i, 'Home']
        rawGames[homeTeam] = scrapeGame(
            my_url=myGames.loc[i, 'HTML Link'],
            game_date=myGames.loc[i, 'Date'],
            home_team_name=myGames.loc[i, 'Home'],
            away_team_name=myGames.loc[i, 'Away'])
        my_count += 1
        if my_count == threshold_25:
            print("Scraped 25% of total games")
        elif my_count == threshold_50:
            print("Scraped 50% of total games")
        elif my_count == threshold_75:
            print("Scraped 75% of total games")
        time.sleep(1)

    print('Number of games scraped = {}'.format(len(rawGames)))

    # Return the uncleaned/raw game dataframes in the dict rawGames
    return rawGames

def cleanSpecificDaysGames(date, rawGames, engine):

    """
     Cleans game dataframes. Removes unwanted columns, renames columns, etc.

     Args:
        date: datetime.date
        rawGames: dictionary - A dictionary linking games to their Dataframes
            keys = home team name (string)
            values = game dataframe returned from function scrapeGame
        engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                                NHL_Database MySQL database

     Returns:
     	None -- Saves cleaned games to 'games' table in MySQL db NHL_Database

     Raises:
     	None
     """

    cleanGames = {}

    print('Number of games to clean = {}'.format(len(rawGames)))

    for homeTeam, game in rawGames.items():
        cleanGames[homeTeam]= cleanGame(game).to_json()

    gamesDF = openMySQLTable('games', engine, myIndex=None)

    for homeTeam, game in cleanGames.items():
        gamesDF.loc[
            (gamesDF['Date'] == str(date)) &
            (gamesDF['Home'] == homeTeam), 'Game'] = str(game)

    # Save gamesDF to MySQL. No need to reset index
    save_mysql_table(gamesDF, 'games', engine, reset_index=False)

    print('Number of games cleaned  = {}'.format(len(cleanGames)))

def updateSpecificDaysLastTime(date, engine):

    """
     Updates MySQL table '2018_2019_LastTime' with the date of the last time
        each player accomplished each feat (scored a goal, registered an assist,
         etc.)

     Args:
        date: datetime.date
        engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                                NHL_Database MySQL database

     Returns:
     	None -- saves data to MySQL table '2018_2019_LastTime'

     Raises:
     	None
     """

    print("Updating Last Time to reflect new stats' dates")

    #Load in last_time_df from the previous day, which will be copied and updated
    lastTime = openMySQLTable('2018_2019_LastTime', engine, myIndex='Player')
    # if 'Backup_Date' in lastTime.columns:
    #     lastTime = lastTime.drop(columns=['Backup_Date'])

    #Load games table; contains strings of cleaned games' DFs as dictionaries
    sqlDF = pd.read_sql(f"SELECT * FROM games WHERE Date = '{date}'", con=engine)

    # Convert dict strings to DFs
    cleanGames = {}
    for i in range(len(sqlDF)):
        homeTeam = sqlDF.loc[i, 'Home']
        gameDictString = sqlDF.loc[i, 'Game']
        gameDict = json.loads(gameDictString)
        cleanGames[homeTeam] = pd.DataFrame.from_dict(gameDict, orient='columns')

    #Set columns to iterate through
    cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    #Also add in last times the player was + or -
    pmCols = ['Plus', 'Minus']

    #Iterate through all games in cleanGames dictionary
    for homeTeam, game_df in cleanGames.items():

        #Create the new index, which is a union of the main one and the one from the specific game
        new_index = lastTime.index.union(game_df.index)
        #Implement the new index, filling in empty values with the date
        # '2000/10/4' (start of '00 season)
        lastTime = lastTime.reindex(new_index, fill_value=datetime.date(2000, 10, 3))
        #Collect the date of the game
        game_date = game_df['Date'].mode()

        #Iterate through columns to update date for goals, assists, etc.
        for column in cols:
            lastTime.loc[game_df[game_df[column] > 0].index, column] = game_date[0]

        #Set Last_Game_Date to current game's date
        lastTime.loc[game_df.index, 'Last_Game_Date'] = game_date[0]

        #Iterate through columns to edit +/- columns
        for column in pmCols:
            if column == 'Plus':
                lastTime.loc[game_df[game_df['+/-'] > 0].index, column] = game_date[0]
            elif column == 'Minus':
                lastTime.loc[game_df[game_df['+/-'] < 0].index, column] = game_date[0]

    #Save only the date, not the time
    for column in lastTime.columns:
        try:
            lastTime[column] = lastTime[column].dt.date
        except AttributeError:
            pass

    # If index has no name, name it
    if lastTime.index.name != 'Player':
        lastTime.index.name = 'Player'

    #Save last_time_df. Reset index.
    save_mysql_table(lastTime, '2018_2019_LastTime', engine, reset_index=True)

def updateSpecificGamesSince(date, engine):

    """
    Updates MySQL table '2018_2019_GamesSince' with the number of games played
        since each player accomplished each feat (scored a goal, registered an
        assist, etc.)

     Args:
        date: datetime.date
        engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                                NHL_Database MySQL database

     Returns:
     	None -- saves data to MySQL table '2018_2019_GamesSince'

     Raises:
     	None
     """

    print("Updating GamesSince to reflect new stats from {}".format(date))

    #Load in GamesSince from the previous day, which will be copied and updated
    GamesSince = openMySQLTable('2018_2019_GamesSince', engine, myIndex='Player')
    if 'Backup_Date' in GamesSince.columns:
        GamesSince = GamesSince.drop(columns=['Backup_Date'])

    #Load cleanGames dictionary
    sqlDF = pd.read_sql(f"SELECT * FROM games WHERE Date = '{date}'", con=engine)

    # Convert dict strings to DFs
    cleanGames = {}
    for i in range(len(sqlDF)):
        homeTeam = sqlDF.loc[i, 'Home']
        gameDictString = sqlDF.loc[i, 'Game']
        gameDict = json.loads(gameDictString)
        cleanGames[homeTeam] = pd.DataFrame.from_dict(gameDict, orient='columns')

    #Set columns to iterate through
    cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    #Also add in last times the player was + or -
    pmCols = ['Plus', 'Minus']

    #Iterate through all games in cleanGames dictionary
    for team, game_df in cleanGames.items():

        #Create the new index, which is a union of the main one and the one from
        # the specific game
        new_index = GamesSince.index.union(game_df.index)
        #Implement the new index, filling in empty values with the value 0
        GamesSince = GamesSince.reindex(new_index, fill_value=0)

        #Iterate through columns to 1 - reset counter to 0 for any stat change
        # and 2 - increment counters for unchanged stats by 1
        for column in cols:
            GamesSince.loc[game_df[game_df[column] > 0].index, column] = 0
            GamesSince.loc[game_df[game_df[column] == 0].index, column] += 1

        #Increment all players' Total Recorded Games by 1
        GamesSince.loc[game_df.index, 'Total Recorded Games'] += 1

        #Iterate through columns to edit +/- columns
        for column in pmCols:
            if column == 'Plus':
                GamesSince.loc[game_df[game_df['+/-'] > 0].index, column] = 0
                GamesSince.loc[game_df[game_df['+/-'] <= 0].index, column] += 1
            elif column == 'Minus':
                GamesSince.loc[game_df[game_df['+/-'] < 0].index, column] = 0
                GamesSince.loc[game_df[game_df['+/-'] >= 0].index, column] += 1

    # If index has no name (as it's new, see for loop above), name it 'Player'
    if GamesSince.index.name != 'Player':
        GamesSince.index.name = 'Player'

    #Save GamesSince. Reset index.
    save_mysql_table(GamesSince, '2018_2019_GamesSince', engine, reset_index=True)

    print('Finished updating GamesSince for {}'.format(date))

def incorporateSpecificDaysStats(date, engine):

    """
     Updates the cumulative statistics for each NHL player from games played on
        the specified date. These data are stored in the table '2018_2019_stats'

     Args:
        date: datetime.date
        engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                                NHL_Database MySQL database

     Returns:
     	None -- saves data to MySQL table '2018_2019_stats'

     Raises:
     	None
     """

    #Load games table; Contains clean games' DFs as dicts as strings
    sqlDF = pd.read_sql(f"SELECT * FROM games WHERE Date = '{date}'", con=engine)

    #Load in the existing myDF selecting 'Player' as the index column
    myDF = openMySQLTable('2018_2019_stats', engine, myIndex='Player')

    # Select columns to add
    columnsToAdd = ['+/-', 'A', 'EV', 'G', 'GW', 'PIM', 'PP', 'PTS', 'S', 'SH',
                    'Shifts', 'TOI']

    # Indicate how many games are incorporated
    print('Adding {} games to myDF'.format(len(sqlDF)))

    # Convert dict strings to DFs and add those to myDF
    cleanGames = {}
    for i in range(len(sqlDF)):
        homeTeam = sqlDF.loc[i, 'Home']
        gameDictString = sqlDF.loc[i, 'Game']
        gameDict = json.loads(gameDictString)
        gameDF = pd.DataFrame.from_dict(gameDict, orient='columns').drop(columns='Team')
        # gameDF['Date'] = len(cleanGames[homeTeam]['Date']) * [date]

        # Add gameDF to myDF (stats)
        myDF[columnsToAdd] = myDF[columnsToAdd].add(gameDF[columnsToAdd], fill_value=0)

    # Convert columns to int
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW',
                      'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        if column in myDF.columns:
            myDF[column] = myDF[column].astype(int)

    # Sort by goals then assists
    myDF = myDF.sort_values(['G', 'A'])

    # Save myDF as the new stats table in MySQL. Reset index.
    save_mysql_table(myDF, '2018_2019_stats', engine, reset_index=True)

'--------------- Aggregate Scraping, Updating Functions ---------------'

def scrapeToToday(engine):

    """
     Scrape games day-by-day, up to current day. Accomodates previously-scraped
        days. Automatically finds last-scraped day. This is the all-encompassing
        function for scraping, cleaning, and storing NHL data.

     Args:
        engine: sqlalchemy.engine.base.Engine - SQLAlchemy engine connection to
                                                NHL_Database MySQL database

     Returns:
     	None

     Raises:
     	None
     """

    # Backup today's tables as pickle files before scraping
    backupTables(engine)

    # Remove unwanted backups
    backups.cleanupBackups()

    #Find last scraped day; indicated by presence of that day's myDF
    date = get_first_unscraped_day(engine)
    today = pd.to_datetime('today').date()

    #Iteratively scrape each day
    while date != today:
        scrapeSpecificDay(date, engine)
        # Find games for this date
        todays_games = findTodaysGames(engine)
        # Only find droughts and make HTML if games are scheduled
        if not todays_games.empty:
            # Find players playing on this date
            todaysPlayerDroughts(todays_games, engine)
            # Make the html for these data
            makeTodaysHTML(engine)
        date += datetime.timedelta(days=1)

    # Also find todays games, todays player droughts, and makes todays HTML
    todaysGames = findTodaysGames(engine)
    todaysPlayerDroughts(todaysGames, engine)
    makeTodaysHTML(engine)

'--------------- Algorithms ---------------'

def KnuthMorrisPratt(pattern, text):

    """
    Finds all the occurrences of the pattern in the text
        and return a list of all positions in the text
        where the pattern starts in the text.

    Args:
     	param1: Type - This is the first param.
     	param2: Type - This is a second param.

    Returns:
     	None - If pattern (swear word) not found in tweet text
        Int - integer index of where the pattern (swear word) begins in the text

    Raises:
     	KeyError: Raises an exception.
    """

    def computePrefix(P):

        """
         Calcuates the prefixes for the Knuth-Morris-Pratt Algorithm, below

         Args:
         	P: string - The pattern (string) to search for within the text

         Returns:
         	S: array - an array that indicates the maximum border for all
                       substrings P[0:i]

         Raises:
         	None
         """

        """ """
        # Create an array, s, that will store the border len for each string, ending at index i
        s = [0] * len(P)

        # Create a border variable to store current max border length
        border = 0

        # Loop through P and update max border for each substring P[0:i]
        for i in range(1, len(P)):
            # While we have a previous border > 0 and the current character doesn't
            # match the next character after the border, reduce border to previous size
            while (border > 0) and (P[i] != P[border]):
                border = s[border - 1]
            # If we have another match, extend border to include new character
            if P[i] == P[border]:
                border += 1
            # If we don't have a match, reset border to 0
            else:
                border = 0
            # Store current border length for P[i] in array s
            s[i] = border

        # Return the array s, which indicates the maximum border for all substrings P[0:i]
        return s

    # Create a master string, S, which has (1) the pattern (2) the symbol "$" and (3) the text
    S = pattern + '$' + text

    # Compute the prefix function for S
    s = computePrefix(S)

    # Create an empty array for the result
    result = list()

    # Loop through s and P, looking for matches
    for i in range(len(pattern)+1, len(S)):
        if s[i] == len(pattern):
            result.append(i - 2*len(pattern))

    if len(result) == 0:
        return None

    return result

'----------------------------------------------------------'
