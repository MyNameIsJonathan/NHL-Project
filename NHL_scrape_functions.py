# Scrape the website https://www.hockey-reference.com for game-by-game stats

import pandas as pd
import pickle
import requests
import datetime
import time
import os
import json
from bs4 import BeautifulSoup
from My_Classes import LengthException
from sqlalchemy import create_engine
from flask import current_app
from flasksite.config import Config


# def backupTables():

#     today = pd.to_datetime('today').date()

#     # Create engines: one for the 'backups' database, one for the current data database
#     backupsEngine = createEngine(database='backups')
#     engine = createEngine(database=None)

#     # Instantiate the current, active dataframes
#     games = openMySQLTable('games', engine)
#     gamesSince = openMySQLTable('2018_2019_GamesSince', engine)
#     lastTime = openMySQLTable('2018_2019_LastTime', engine)
#     stats = openMySQLTable('2018_2019_stats', engine)

#     # Instantiate the MySQL databases as pandas dataframes, for editing
#     gamesBackup = openMySQLTable('gamesBackup', backupsEngine)
#     gamesSinceBackup = openMySQLTable('gamesSinceBackup', backupsEngine)
#     lastTimeBackup = openMySQLTable('lastTimeBackup', backupsEngine)
#     statsBackup = openMySQLTable('statsBackup', backupsEngine)

#     # Add today's date in a new column, 'Backup_Date', to the current, active DFs
#     games['Backup_Date'] = today
#     gamesSince['Backup_Date'] = today
#     lastTime['Backup_Date'] = today
#     stats['Backup_Date'] = today

#     # Concat the current backups with the new rows from the current active DFs
#     gamesBackup = pd.concat([gamesBackup, games])
#     gamesSinceBackup = pd.concat([gamesSinceBackup, gamesSince])
#     lastTimeBackup = pd.concat([lastTimeBackup, lastTime])
#     statsBackup = pd.concat([statsBackup, stats])

#     # Update backup tables in MySQL backups database
#     gamesBackup.to_sql(
#         name='gamesBackup',
#         con=backupsEngine,
#         index=False,
#         if_exists='replace')

#     gamesSinceBackup.to_sql(
#         name='gamesSinceBackup',
#         con=backupsEngine,
#         index=False,
#         if_exists='replace')

#     lastTimeBackup.to_sql(
#         name='lastTimeBackup',
#         con=backupsEngine,
#         index=False,
#         if_exists='replace')

#     statsBackup.to_sql(
#         name='statsBackup',
#         con=backupsEngine,
#         index=False,
#         if_exists='replace')

def getResetDate(backupsEngine, desiredDate='2019-02-05'):

    print(f'Resetting to {desiredDate}')

    # Convert desiredDate to datetime.date
    desiredDate = pd.to_datetime(desiredDate, format='%Y-%m-%d').date()

    # Load in a table, find the list of backup dates
    df = openMySQLTable('gamesSinceBackup', backupsEngine)
    myDates = list(df['Backup_Date'].dt.date.unique())

    # See if desiredDate is in the list; if not, find next latest date
    if desiredDate in myDates:
        return desiredDate
    # If desiredDate is older than oldest available date, return oldest available date
    elif desiredDate < min(myDates):
        return min(myDates)
    # Else find next oldest date, after desiredDate
    else:
        nextDate = (pd.to_datetime(desiredDate, format='%Y-%m-%d') - datetime.timedelta(days=1)).date()
        while nextDate not in myDates:
            nextDate -= datetime.timedelta(days=1)
        return pd.Timestamp(nextDate)

def resetToDay(engine, backupsEngine, date='2019-02-05'):

    # 1 - Revert games, gamesSince, and LastTime to former values, from backups

    # Instantiate the MySQL databases as pandas dataframes, for editing
    gamesSinceBackup = openMySQLTable('gamesSinceBackup', backupsEngine)
    lastTimeBackup = openMySQLTable('lastTimeBackup', backupsEngine)
    statsBackup = openMySQLTable('statsBackup', backupsEngine)

    # Get the date thats =(or older than) the specified reset date
    myResetDate = getResetDate(backupsEngine, date)

    # Slice backup DFs by myResetDate to get the reverted DFs
    gamesSince = gamesSinceBackup.loc[gamesSinceBackup['Backup_Date'].dt.date == myResetDate]
    lastTime = lastTimeBackup.loc[lastTimeBackup['Backup_Date'].dt.date == myResetDate]
    stats = statsBackup.loc[statsBackup['Backup_Date'].dt.date == myResetDate]

    # 2 - Reset 'game' column of games to None for dates between specified date and today

    # Establish the date range, as strings
    myDate = pd.to_datetime(date, format='%Y-%m-%d').date()
    today = pd.to_datetime('today').date()
    myDateRange = [day.date() for day in pd.date_range(myDate, today)]

    # No 'gamesBackup' needed, as the 'game' column only needs to be reset to 'None'
    games = openMySQLTable('games', engine)

    # Fill 'None' into games for specified date range
    mylength = len(games.loc[games['Date'].isin(myDateRange), 'Game'])
    games.loc[games['Date'].isin(myDateRange), 'Game'] = [None] * mylength

    # 3 - Save the resulting DataFrames in MySQL, replacing the old tables

    gamesSince.to_sql(
        name='2018_2019_GamesSince',
        con=engine,
        index=False,
        if_exists='replace')

    lastTime.to_sql(
        name='2018_2019_LastTime',
        con=engine,
        index=False,
        if_exists='replace')

    stats.to_sql(
        name='2018_2019_stats',
        con=engine,
        index=False,
        if_exists='replace')

    games.to_sql(
        name='games',
        con=engine,
        index=False,
        if_exists='replace')


'--------------- MySql Functions ---------------'

def nonFlaskCreateEngine():

    """[ Opens a connection to the provided table in the NHL Stats MySQL Database]

    Returns:
        [ sqlalchemy.engine.base.Engine ] -- [ A connection to the NHL MySQL Database for the given table]
    """

    myConfig = Config()

    MYSQL_DATABASE = myConfig.MYSQL_DATABASE_DB
    MYSQL_PASSWORD = myConfig.MYSQL_DATABASE_PASSWORD
    MYSQL_PORT = myConfig.MYSQL_DATABASE_PORT
    MYSQL_HOST = myConfig.MYSQL_DATABASE_HOST
    MYSQL_USER = myConfig.MYSQL_DATABASE_USER

    engine = create_engine(f'mysql+mysqldb://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}')

    print('MySQL Connection Engine successfully created')

    return engine

def createEngine(database=None):

    """[ Opens a connection to the provided table in the NHL Stats MySQL Database]

    Returns:
        [ sqlalchemy.engine.base.Engine ] -- [ A connection to the NHL MySQL Database for the given table]
    """

    MYSQL_DATABASE = current_app.config['MYSQL_DATABASE_DB']
    MYSQL_PASSWORD = current_app.config['MYSQL_DATABASE_PASSWORD']
    MYSQL_PORT = current_app.config['MYSQL_DATABASE_PORT']
    MYSQL_HOST = current_app.config['MYSQL_DATABASE_HOST']
    MYSQL_USER = current_app.config['MYSQL_DATABASE_USER']

    engine = create_engine(f'mysql+mysqldb://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}')

    print('MySQL Connection Engine successfully created')

    return engine

def getFirstUnscrapedDay(engine):

    """[ Uses the 'games' MySQL table to find the latest day whose games are not yet scraped]

    Returns:
        [ datetime.date ] -- [ Date of latest day whose games are not yet scraped ]
    """

    print('Finding first unscraped day')

    games = openMySQLTable('games', engine)
    unscrapedDays = games.loc[games['Game'].isnull()]
    firstUnscrapedDay = unscrapedDays.loc[:, 'Date'].min().date()

    print(f'First unscraped day successfully found: {firstUnscrapedDay}')

    return firstUnscrapedDay

def openTodaysDroughts(engine):

    print('Opening todaysDroughts DF')

    today = pd.to_datetime('today').date()

    todaysDroughts = engine.execute(f"SELECT * FROM todaysDroughts WHERE Date = '{today}'").fetchone()

    print('todaysDroughts DF opened successfully')

    return todaysDroughts

def openMySQLTable(table_name, engine):

    if table_name == 'games':
        return pd.read_sql_table('games', engine, parse_dates=['Date'])
    elif table_name == '2018_2019_GamesSince':
        return pd.read_sql_table('2018_2019_GamesSince', engine)
    elif table_name == '2018_2019_LastTime':
        return pd.read_sql_table('2018_2019_LastTime', engine, parse_dates=['G', 'A', 'PTS', 'Plus', 'Minus', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Last_Game_Date', 'Last Game Date'])
    elif table_name == '2018_2019_stats':
        return pd.read_sql_table('2018_2019_stats', engine)
    elif table_name == 'gamesBackup':
        return pd.read_sql_table('gamesBackup', engine)
    elif table_name == 'gamesSinceBackup':
        return pd.read_sql_table('gamesSinceBackup', engine)
    elif table_name == 'lastTimeBackup':
        return pd.read_sql_table('lastTimeBackup', engine)
    elif table_name == 'statsBackup':
        return pd.read_sql_table('statsBackup', engine)
    elif table_name == 'todaysDroughts':
        return pd.read_sql_table('todaysDroughts', engine)
    elif table_name == 'dailyDataFrames':
        return pd.read_sql_table('dailyDataFrames', engine)
    elif table_name == 'stamkosTweets':
        return pd.read_sql_table('stamkosTweets', engine)

'--------------- Single-Game-Specific Functions ---------------'

def getURLS(date):

    """[Uses the given date to create the html links to www.hockey-reference.com for that day's games.
        Scrapes that website and creates the link for each of the games on that day]

    Returns:
        [list] -- [boxscore_links : html links to the boxscores for each game of each day]
        [list] -- [my_home_teams : list of home teams. The ith game's home team is in the ith position in this list]
        [list] -- [my_away_teams : list of away teams. The ith game's away team is in the ith position in this list]
        [list] -- [my_game_dates : dates for each game. ith game is in ith position in this list]
    """

    print(f'Getting URLs for date: {date}')

    # Create the hockey-reference link for the day's games
    url = 'https://www.hockey-reference.com/boxscores/index.fcgi?month={}&day={}&year={}'.format(date.month, date.day, date.year)

    # Record team names for each game
    my_days_games = pd.read_html(url)
    my_home_teams = []
    my_away_teams = []
    my_date = str(year) + '/' + str(month) + '/' + str(day)
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

    # Return 1 - boxscore links, 2 - home team names, 3 - away team names, 4 - game dates
    return (boxscore_links, my_home_teams, my_away_teams, my_game_dates)

def scrapeGame(my_url, game_date, home_team_name, away_team_name):

    """[Pulls stats from a single game, given the url (attained through getURLS), the date (also from getURLS), home and away teams]
    Returns:
        [Pandas DataFrame] -- [a clean df that has the game's stats]
    """

    # Read table from hockey-reference
    df_list = pd.read_html(my_url, header=1)

    #Select only teams' stats DataFrames, as the penalty dataframe will not exist if there are no penalties, causing indexing issues otherwise
    myDFs = []
    for df in df_list:
        if 'G' in df.columns:
            myDFs.append(df)
    df_away = myDFs[0].iloc[:-1, 1:18]
    df_home = myDFs[1].iloc[:-1, 1:18]

    # Make 'Team' column
    df_away['Team'] = away_team_name
    df_home['Team'] = home_team_name

    #Combine the two teams' dataframes
    df = pd.concat([df_away, df_home], sort=True)

    #Make a 'Date' column, which will eventually be used to represent the last time each player scored a goal
    df['Date'] = game_date
    df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d')
    df['Date'] = df['Date'].dt.date

    # Set player name to index
    df = df.set_index('Player')

    return df

def cleanGame(game_df):

    """ Cleans individual game data """

    # Delete columns that are only present in the datasets starting in 2014-2015 season
    cols_to_drop = ['EV.1', 'PP.1', 'SH.1', 'S%', 'EV.2', 'PP.2', 'SH.2', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17']
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
    """Get today's date and create url, date string, and scrape data"""

    today = pd.to_datetime('today').date()

    games = openMySQLTable('games', engine)

    return games[games['Date'] == str(today)]

def todaysPlayerDroughts(todaysGames, engine):
    """Get stats for players who play today
    Input: my_date; type: string; format: "yyyy-mm-dd" """

    today = pd.to_datetime('today').date()

    #Get the list of teams playing today
    teams_playing_today = list(todaysGames['Home'].unique()) + list(todaysGames['Away'].unique())

    #Fill players_playing_today by iterating through the team-player dictionary from the file team_creation.py
    NHL_teams_and_players = pd.read_pickle('/home/jonathan/NHL-Project/pickleFiles/Teams/NHL_teams_and_players.pickle')

    #Instantiate a list of player names who play today and fill it
    players_playing_today = []
    for team in teams_playing_today:
        players_playing_today.extend([player.Name for player in NHL_teams_and_players[team]])
    players_playing_today = pd.Series(players_playing_today).unique()

    #Save how many players are playing today
    numberOfPlayersToday = len(players_playing_today)

    #Open yesterday's GamesSince df to see the games since each of today's players scored, etc.
    GamesSince = openMySQLTable('2018_2019_GamesSince', engine).set_index('Player')
    todays_GamesSince = GamesSince.loc[players_playing_today, :]

    # Open yesterday's lastTimeDF
    lastTime = openMySQLTable('2018_2019_LastTime', engine).set_index('Player')
    todays_lastTime = lastTime.loc[players_playing_today, :]

    #Save the top 5 players for each category of GamesSince, such as the 5 players who haven't scored in the most games
    todaysDroughts = {}

    #Select all columns except Total Recorded Games
    myColumns = ['G', 'A', 'PTS', 'Plus', 'Minus', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    # Loop through columns to select oldest feat for each. Skip player if they've never accomplished selected feat within
    # the dates of my dataset (my dataset spans 2000-10-4 and later, so date='2000-10-3')
    null_date = pd.to_datetime('2000-10-3', format="%Y-%m-%d").date()
    for column in myColumns:
        myAvailablePlayers = todays_lastTime.loc[todays_lastTime[column].dt.date > null_date].index
        mySlice = todays_GamesSince.loc[myAvailablePlayers, :]
        myPlayer = mySlice.loc[mySlice[column] == mySlice[column].max()].index[0]
        myDate = mySlice.loc[myPlayer, column]

        todaysDroughts[column] = [myPlayer, todays_GamesSince.loc[myPlayer, column], str(myDate)]

    #Save the dictionary, todaysDroughts, for uploading on website
    droughtsDF =  openMySQLTable('todaysDroughts', engine)
    newRow = pd.Series({
        'id': droughtsDF['id'].max() + 1,
        'Date': today,
        'todaysDroughts': todaysDroughts,
        'numberOfPlayersToday': numberOfPlayersToday})
    droughtsDF = droughtsDF.append(newRow, ignore_index=True)

    droughtsDF.to_sql(
        name='todaysDroughts',
        con=engine,
        index=False,
        if_exists='replace')

def makeTodaysHTML(engine):

    # Load in the three main dataframes and select for current players, if necessary
    stats = openMySQLTable('2018_2019_stats', engine).set_index('Player')
    lastTime = openMySQLTable('2018_2019_LastTime', engine).set_index('Player')
    gamesSince = openMySQLTable('2018_2019_GamesSince', engine).set_index('Player')

    # Clean myDF
    stats['TOI'] = stats['TOI'].astype(int)
    stats = stats.sort_values(['G', 'PTS'], ascending=False)
    stats = stats.reindex(['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Shifts', 'TOI'], axis=1)

    # Clean lastTime
    lastTime = lastTime[lastTime['Last Game Date'].dt.date >= pd.to_datetime('2018-7-1', format="%Y-%m-%d").date()] # Select for players who've played in last 30 days only
    lastTime = lastTime[lastTime['G'].dt.date > pd.to_datetime('2000-10-03', format="%Y-%m-%d").date()] # Players who've never scored have last goal set as 2000/10/3. Remove these players
    lastTime = lastTime.sort_values(['G', 'A'])
    lastTime = lastTime.reindex(['Last Game Date', 'G', 'A', 'PTS', 'Plus' 'Minus', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S'], axis=1)

    # Grab the players in this df, for slicing retired players from the gamesSince DF
    currentPlayers = lastTime.index
    gamesSince = gamesSince.reindex(currentPlayers)
    gamesSince = gamesSince.sort_values(['G', 'A'], ascending=False)

    # Replace date '2000-10-3' with 'Never'
    stats = stats.replace(to_replace=pd.to_datetime('2000-10-3', format="%Y-%m-%d").date(), value='Never')
    lastTime = lastTime.replace(to_replace=pd.to_datetime('2000-10-3', format="%Y-%m-%d").date(), value='Never')
    gamesSince = gamesSince.replace(to_replace=pd.to_datetime('2000-10-3', format="%Y-%m-%d").date(), value='Never')

    # Set pandas options
    pd.set_option('colheader_justify', 'center')

    # Save the HTML strings in a dictionary, to be loaded on routes.py file for display. This prevents it from being calculated everytime the user is routed to "Today's Players"
    statsJSON = stats.iloc[:10, :].to_json()
    lastTimeJSON = lastTime.iloc[:10, :].to_json()
    gamesSinceJSON = gamesSince.iloc[:10, :].to_json()

    # Save JSONs of the three dataframes in the MySQL DB table = dailyDataFrames;
    dailyDataFrames = openMySQLTable('dailyDataFrames', engine)
    newRow = pd.Series({
        'id': len(dailyDataFrames) + 1,
        'date': pd.to_datetime('today').date(),
        'stats': statsJSON,
        'lastTime': lastTimeJSON,
        'gamesSince': gamesSinceJSON})
    dailyDataFrames = dailyDataFrames.append(newRow, ignore_index=True)

    # Save the DF to the MySQL database
    dailyDataFrames.to_sql(
        name='dailyDataFrames',
        con=engine,
        index=False,
        if_exists='replace')

def opentodaysHTML(engine):

    # Get the last row of the table, sorted by date. This means itll be today's html, unless there was an error, allowing it to fall back on yesterdays html
    myHTML = engine.execute(f"SELECT * FROM dailyDataFrames ORDER BY date DESC LIMIT 1").fetchone()

    # Select each component from myHTML (index: value --> 0: id, 1: date, 2: mydf, 3: lastTime, 4: gamesSince). Convert these dicts to DataFrames
    mydf = pd.DataFrame.from_dict(json.loads(myHTML['stats']))
    lastTime = pd.DataFrame.from_dict(json.loads(myHTML['lastTime']))
    gamesSince = pd.DataFrame.from_dict(json.loads(myHTML['gamesSince']))

    # Convert DFs to html
    myDFHTML = mydf.head(10).to_html(classes=['table', 'stat-table'], index_names=False, justify='center')
    lastTimeHTML = lastTime.head(10).to_html(classes=['table', 'stat-table'], index_names=False, justify='center')
    gamesSinceHTML = gamesSince.head(10).to_html(classes=['table', 'stat-table'], index_names=False, justify='center')

    todaysHTML = {
        'myDF': myDFHTML,
        'lastTime': lastTimeHTML,
        'gamesSince': gamesSinceHTML}

    return todaysHTML

'--------------- Single-Day Scrape Functions ---------------'

def scrapeSpecificDaysURLS(engine, date):

    """[scrapes all html links for the given date returning them as a pandas DF'.
    """

    daysGames = pd.read_sql_query(f"SELECT * FROM games WHERE Date = '{date}'", con=engine)

    daysGames['Game Number'] = daysGames['Game Number'].astype(int)

    if len(daysGames) == 0:
        return 'No Games Found'
    else:
        return daysGames

def scrapeSpecificDaysGames(date, myGames):

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

    cleanGames = {}

    print('Number of games to clean = {}'.format(len(rawGames)))

    for homeTeam, game in rawGames.items():
        cleanGames[homeTeam]= cleanGame(game).to_json()

    gamesDF = openMySQLTable('games', engine)

    for homeTeam, game in cleanGames.items():
        gamesDF.loc[(gamesDF['Date'] == str(date)) & (gamesDF['Home'] == homeTeam), 'Game'] = str(game)

    gamesDF.to_sql(
        name='games',
        con=engine,
        index=False,
        if_exists='replace')

    print('Number of games cleaned  = {}'.format(len(cleanGames)))

def updateSpecificDaysLastTime(date, engine):

    print("Updating Last Time to reflect new stats' dates")

    #Load in last_time_df from the previous day, which will be copied and updated
    lastTime = openMySQLTable('2018_2019_LastTime', engine).set_index('Player')
    if 'Backup_Date' in lastTime.columns:
        lastTime = lastTime.drop(columns=['Backup_Date'])

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
        #Implement the new index, filling in empty values with the date '2000/10/4' (start of '00 season)
        lastTime = lastTime.reindex(new_index, fill_value=datetime.date(2000,10,3))
        #Collect the date of the game
        game_date = game_df['Date'].mode()

        #Iterate through columns to update date for goals, assists, etc.
        for column in cols:
            lastTime.loc[game_df[game_df[column] > 0].index, column] = game_date[0]

        #Set last game date to current game's date
        lastTime.loc[game_df.index, 'Last Game Date'] = game_date[0]

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

    # Reset index of lastTime
    lastTime = lastTime.reset_index()

    #Save last_time_df
    lastTime.to_sql(
        name='2018_2019_LastTime',
        con=engine,
        index=False,
        if_exists='replace')

def updateSpecificGamesSince(date, engine):

    print("Updating GamesSince to reflect new stats from {}".format(date))

    #Load in GamesSince from the previous day, which will be copied and updated
    GamesSince = openMySQLTable('2018_2019_GamesSince', engine).set_index('Player')
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

        #Create the new index, which is a union of the main one and the one from the specific game
        new_index = GamesSince.index.union(game_df.index)
        #Implement the new index, filling in empty values with the value 0
        GamesSince = GamesSince.reindex(new_index, fill_value=0)

        #Iterate through columns to 1 - reset counter to 0 for any stat change and 2 - increment counters for unchanged stats by 1
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

    #Reset index got GamesSince
    GamesSince = GamesSince.reset_index()

    #Save GamesSince
    GamesSince.to_sql(
        name='2018_2019_GamesSince',
        con=engine,
        index=False,
        if_exists='replace')

    print('Finished updating GamesSince for {}'.format(date))

def incorporateSpecificDaysStats(date, engine):

    #Load games TABLE; Contains clean games' DFs as dicts as strings
    sqlDF = pd.read_sql(f"SELECT * FROM games WHERE Date = '{date}'", con=engine)

    # Convert dict strings to DFs
    cleanGames = {}
    for i in range(len(sqlDF)):
        homeTeam = sqlDF.loc[i, 'Home']
        gameDictString = sqlDF.loc[i, 'Game']
        gameDict = json.loads(gameDictString)
        cleanGames[homeTeam] = pd.DataFrame.from_dict(gameDict, orient='columns').drop(columns='Team')
        cleanGames[homeTeam]['Date'] = len(cleanGames[homeTeam]['Date']) * [date]

    print('Adding {} games to myDF'.format(len(cleanGames)))

    #Load in the existing myDF selecting 'Player' as the index column
    myDF = pd.read_sql('2018_2019_stats', con=engine, index_col='Player')
    if 'Backup_Date' in myDF.columns:
        myDF = myDF.drop(columns=['Backup_Date'])

    #Create main df for all day's games
    newDF = pd.concat([game for game in cleanGames.values()], sort=True)
    newDF = newDF.groupby(newDF.index).sum()
    newDF['Backup_Date'] = None
    columnsToAdd = ['+/-', 'A', 'EV', 'G', 'GW', 'PIM', 'PP', 'PTS', 'S', 'SH', 'Shifts', 'TOI']

    #Combine myDF and newDF
    myDF[columnsToAdd] = myDF[columnsToAdd].add(newDF[columnsToAdd], fill_value=0)

    # Convert columns to int
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        if column in myDF.columns:
            myDF[column] = myDF[column].astype(int)

    # Reset the index column
    myDF = myDF.reset_index()

    # Save myDF as the new stats table in MySQL
    myDF.to_sql(
        name='2018_2019_stats',
        con=engine,
        index=False,
        if_exists='replace')

'--------------- Aggregate Scraping, Updating Functions ---------------'

def scrapeSpecificDay(date, engine):

    """ Scrape, clean, incorporate specific day's stats """

    # Scrape URLs for the given date
    myGames = scrapeSpecificDaysURLS(engine, date)
    # Scrape the games from those URLs
    rawGames = scrapeSpecificDaysGames(date, myGames)
    # Clean the games' DFs
    cleanSpecificDaysGames(date, rawGames, engine)
    # Update the lastTime, gamesSince, and Overall Statistics tables in MySQL
    updateSpecificDaysLastTime(date, engine)
    updateSpecificGamesSince(date, engine)
    incorporateSpecificDaysStats(date, engine)

def scrapeToToday(engine):
    """Scrape games day-by-day, up to current day
    Accomodates previously-scraped days. Automatically finds last-scraped day"""

    #Find last scraped day; indicated by presence of that day's myDF
    date = getFirstUnscrapedDay(engine)
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

    Find all the occurrences of the pattern in the text
    and return a list of all positions in the text
    where the pattern starts in the text.

    Returns None if pattern not found in text, else returns
    the 0-based indices of where the pattern begins within the text

    """

    def computePrefix(P):
        """Calcuates the prefixes for the Knuth-Morris-Pratt Algorithm, below """
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
    else:
        return result

'----------------------------------------------------------'


# engine = createEngine()
# backupsEngine = createEngine(database='backups')

# resetToDay(engine, backupsEngine, date='2019-02-05')

# scrapeToToday(engine)

''' Helpful table backups

gs = openMySQLTable('2018_2019_GamesSince', engine)
lt = openMySQLTable('2018_2019_LastTime', engine)
stats = openMySQLTable('2018_2019_stats', engine)
games = openMySQLTable('games', engine)

gsb = openMySQLTable('gamesSinceBackup', backupsEngine)
ltb = openMySQLTable('lastTimeBackup', backupsEngine)
statsb = openMySQLTable('statsBackup', backupsEngine)

gs = pd.read_pickle('/home/jonathan/NHL-Project/gamesSinceDefault.pickle').reset_index()
lt = pd.read_pickle('/home/jonathan/NHL-Project/lastTimeDefault.pickle').reset_index()
stats = pd.read_pickle('/home/jonathan/NHL-Project/statsDefault.pickle').reset_index()
games = pd.read_pickle('/home/jonathan/NHL-Project/gamesDefault.pickle')

gsb = pd.read_pickle('/home/jonathan/NHL-Project/gamesSinceBackupDefault.pickle')
ltb = pd.read_pickle('/home/jonathan/NHL-Project/lastTimeBackupDefault.pickle')
statsb = pd.read_pickle('/home/jonathan/NHL-Project/statsBackupDefault.pickle')


gs.to_sql(
    name='2018_2019_GamesSince',
    con=engine,
    index=False,
    if_exists='replace')

lt.to_sql(
    name='2018_2019_LastTime',
    con=engine,
    index=False,
    if_exists='replace')

stats.to_sql(
    name='2018_2019_stats',
    con=engine,
    index=False,
    if_exists='replace')

games.to_sql(
    name='games',
    con=engine,
    index=False,
    if_exists='replace')


gsb.to_sql(
    name='gamesSinceBackup',
    con=backupsEngine,
    index=False,
    if_exists='replace')

ltb.to_sql(
    name='lastTimeBackup',
    con=backupsEngine,
    index=False,
    if_exists='replace')

statsb.to_sql(
    name='statsBackup',
    con=backupsEngine,
    index=False,
    if_exists='replace')


'''
