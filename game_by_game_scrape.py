# Scrape the website https://www.hockey-reference.com for game-by-game stats

import pandas as pd
import pickle
import requests
from bs4 import BeautifulSoup
from My_Classes import LengthException
import datetime
import time
import os.path


'--------------- Single-Game-Specific Functions ---------------'

def getURLS(month, day, year):

    """[Function to use the given date to create the html links to www.hockey-reference.com for that day's games. 
        Scrapes that website and creates the link for each of the games on that day]
    
    Returns:
        [list] -- [boxscore_links : html links to the boxsxcores for each game of each day]
        [list] -- [my_home_teams : list of home teams. The ith game's home team is in the ith position in this list]
        [list] -- [my_away_teams : list of away teams. The ith game's away team is in the ith position in this list]
        [list] -- [my_game_dates : dates for each game. ith game is in ith position in this list]
    """

    # Create the hockey-reference link for the day's games
    url = 'https://www.hockey-reference.com/boxscores/index.fcgi?month={}&day={}&year={}'.format(month, day, year)

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

    """[Function to pull stats from a single game, given the url (attained through getURLS), the date (also from getURLS), home and away teams]
    Returns:
        [Pandas DataFrame] -- [a clean df that has the game's stats]
    """

    # Read table from hockey-reference
    df_list = pd.read_html(my_url, header=1)
    
    #Select only teams' stats DataFrames, as the penalty dataframe will not exist if there are no penalties, causing indexing issues otherwise
    my_dfs = []
    for df in df_list:
        if 'G' in df.columns:
            my_dfs.append(df)
    df_away = my_dfs[0].iloc[:-1, 1:18]
    df_home = my_dfs[1].iloc[:-1, 1:18]

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

    # Copy df for editing
    df = game_df.copy(deep=True)

    # Delete columns that are only present in the datasets starting in 2014-2015 season
    cols_to_drop = ['EV.1', 'PP.1', 'SH.1', 'S%', 'EV.2', 'PP.2', 'SH.2', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17']
    df = df.drop([column for column in cols_to_drop if column in df.columns], axis=1)

    # Rename columns for better readability
    df = df.rename(columns = {'SHFT':'Shifts'})

    #Fill NaN values to convert to int
    df = df.fillna(0)

    #Get int of minutes on ice from string "mm:ss"
    df['TOI'] = df['TOI'].str.split(':')
    df['TOI'] = df['TOI'].apply(lambda x: int(x[0]) + int(x[1])/60)
    df['TOI'] = df['TOI'].round(2)
    
    return df

'--------------- Todays Games Functions ---------------'

def findTodaysGames():
    """Get today's date and create url, date string, and scrape data"""
    today = pd.to_datetime('today').date()
    url = 'https://www.hockey-reference.com/leagues/NHL_2019_games.html' #Change this url for '19-'20 season
    my_games_df = pd.read_html(url)[0]
    my_games_df = my_games_df[['Date', 'Home', 'Visitor']]
    my_games_df = my_games_df[my_games_df['Date'] == str(today)]
    #Save todaysGames df with the date
    savePickle(my_games_df, 'todaysGames_{}'.format(str(today)))

def todaysPlayersStats():
    """Get stats for players who play today"""
    today = pd.to_datetime('today').date()
    todaysGames = pd.read_pickle('todaysGames_{}.pickle'.format(str(today)))
    #Get the list of teams playing today
    teams_playing_today = list(todaysGames['Home'].unique()) + list(todaysGames['Visitor'].unique())

    #Fill players_playing_today by iterating through the team-player dictionary from the file team_creation.py
    NHL_teams_and_players = pd.read_pickle('Teams/NHL_teams_and_players.pickle')

    #Instantiate a list of player names who play today and fill it 
    players_playing_today = []
    for team in teams_playing_today:
        players_playing_today.extend([player.Name for player in NHL_teams_and_players[team]])

    #Open the GamesSince df to see the games since each of today's players scored, etc.
    GamesSince = pd.read_pickle('dailyGamesSince/dailyGamesSince_{}.pickle'.format(today - datetime.timedelta(days=1)))
    todays_GamesSince = GamesSince.reindex(players_playing_today, fill_value=0)

    #Print the top 5 players for each category of GamesSince, such as the 5 players who haven't scored in the most games
    for column in todays_GamesSince.columns:
        todays_GamesSince = todays_GamesSince.sort_values(column, ascending=False)
        print(todays_GamesSince.head(1))
        print('')

'--------------- Single-Day Scrape Functions ---------------'

def scrapeSpecificDaysURLS(date='2000-12-31'):

    """[scrapes all html links for the given date storing them in a piclkle file labeled by day'.
    """

    myDate = pd.to_datetime(date, format='%Y-%m-%d').date()

    daily_html_links = {}

    total_home_teams = []
    total_away_teams = []
    all_game_dates = []

    print('Scraping game links for games on {}'.format(myDate))

    # Get the html links for the tables
    my_html_results = getURLS(myDate.month, myDate.day, myDate.year)
    daily_html_links[str(myDate)] = my_html_results[0]
    total_home_teams.extend(my_html_results[1])
    total_away_teams.extend(my_html_results[2])
    all_game_dates.extend(my_html_results[3])

    # Pickle the 'daily_html_links' dict using the highest protocol available.
    savePickle(daily_html_links, 'dailyHTMLLinks/dailyHTMLLinks_{}'.format(myDate))

    # Flatten list of game htmls
    flat_list_game_links = [item for sublist in list(daily_html_links.values()) for item in sublist]

    #Save home teams, away teams, and game dates in df
    teams_and_dates = pd.DataFrame([total_home_teams, total_away_teams, all_game_dates, flat_list_game_links])
    teams_and_dates = teams_and_dates.transpose()
    savePickle(teams_and_dates, 'dailyTeamsAndDates/dailyTeamsAndDates_{}'.format(myDate))

    print('Total game links scraped = {}'.format(len(teams_and_dates)))

    if len(teams_and_dates) == 0:
        return 'No Games Found'
    else:
        return 'Games Found'
    
def scrapeSpecificDaysGames(date='2000-1-1'): 

    myDate = pd.to_datetime(date, format='%Y-%m-%d').date()

    #Create my_games_unclean dict to store scraped games
    dailyGamesUnclean = {}

    daysGames = pd.read_pickle('dailyTeamsAndDates/dailyTeamsAndDates_{}.pickle'.format(myDate))
    number_of_games = len(daysGames)
    print('Number of games to scrape = {}'.format(number_of_games))

    #Instantiate counter for reporting scrape progress and create % thresholds
    my_count = 0
    threshold_25 = int(number_of_games*0.25)
    threshold_50 = int(number_of_games*0.5)
    threshold_75 = int(number_of_games*0.75)

    # Use  html links to create games' dataframes
    for game in range(number_of_games):
        dailyGamesUnclean[game] = scrapeGame(
            my_url=daysGames.iloc[game, 3], 
            game_date=daysGames.iloc[game, 2],
            home_team_name=daysGames.iloc[game, 0],
            away_team_name=daysGames.iloc[game, 1])
        my_count += 1
        if my_count == threshold_25:
            print("Scraped 25% of total games")
        elif my_count == threshold_50:
            print("Scraped 50% of total games")
        elif my_count == threshold_75:
            print("Scraped 75% of total games")
        time.sleep(1)
    
    # Pickle the 'my_games' dictionary using the highest protocol available.
    savePickle(dailyGamesUnclean, 'dailyGamesUnclean/dailyGamesUnclean_{}'.format(myDate))

    print('Number of games scraped = {}'.format(len(dailyGamesUnclean)))

def cleanSpecificDaysGames(date='2000-1-1'):

    myDate = pd.to_datetime(date, format='%Y-%m-%d').date()

    my_games_unclean = pd.read_pickle('dailyGamesUnclean/dailyGamesUnclean_{}.pickle'.format(myDate))
    my_games_clean = {}

    print('Number of games to clean = {}'.format(len(my_games_unclean)))

    for index, game in my_games_unclean.items():
        my_games_clean[index] = cleanGame(game)

    savePickle(my_games_clean, 'dailyGamesClean/dailyGamesClean_{}'.format(myDate))

    print('Number of games cleaned  = {}'.format(len(my_games_clean)))

def updateSpecificDaysLastTime(date='2000-1-1'):

    print("Updating Last Time to reflect new stats' dates")

    myDate = pd.to_datetime(date, format='%Y-%m-%d').date()

    #Load in last_time_df from the previous day, which will be copied and updated
    last_time_df = pd.read_pickle('dailyLastTime/dailyLastTime_{}.pickle'.format(myDate - datetime.timedelta(days=1))).copy()

    #Load my_games_clean dictionary
    my_games_clean = pd.read_pickle('dailyGamesClean/dailyGamesClean_{}.pickle'.format(myDate))

    #Set columns to iterate through
    cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    #Also add in last times the player was + or -
    pmCols = ['+', '-']

    #Iterate through all games in my_games_clean dictionary
    for index, game_df in my_games_clean.items():

        #Create the new index, which is a union of the main one and the one from the specific game
        new_index = last_time_df.index.union(game_df.index)
        #Implement the new index, filling in empty values with the date '2000/10/4' (start of '00 season)
        last_time_df = last_time_df.reindex(new_index, fill_value=datetime.date(2000,10,3))
        #Collect the date of the game
        game_date = game_df['Date'].mode()

        #Iterate through columns to update date for goals, assists, etc.
        for column in cols:
            last_time_df.loc[game_df[game_df[column] > 0].index, column] = game_date[0]

        #Set last game date to current game's date
        last_time_df.loc[game_df.index, 'Last Game Date'] = game_date[0]

        #Iterate through columns to edit +/- columns
        for column in pmCols:
            if column == '+':
                last_time_df.loc[game_df[game_df['+/-'] > 0].index, column] = game_date[0]
            elif column == '-':
                last_time_df.loc[game_df[game_df['+/-'] < 0].index, column] = game_date[0]

    #Save only the date, not the time
    for column in last_time_df.columns:
        try:
            last_time_df[column] = last_time_df[column].dt.date
        except AttributeError:
            pass

    #Save last_time_df
    savePickle(last_time_df, 'dailyLastTime/dailyLastTime_{}'.format(myDate))

def updateSpecificDaysSince(date='2000-1-1'):

    myDate = pd.to_datetime(date, format='%Y-%m-%d').date()

    print("Updating GamesSince to reflect new stats from {}".format(myDate))

    #Load in GamesSince from the previous day, which will be copied and updated
    GamesSince = pd.read_pickle('dailyGamesSince/dailyGamesSince_{}.pickle'.format(myDate - datetime.timedelta(days=1))).copy()

    #Load my_games_clean dictionary
    my_games_clean = pd.read_pickle('dailyGamesClean/dailyGamesClean_{}.pickle'.format(myDate))

    #Set columns to iterate through
    cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    #Also add in last times the player was + or -
    pmCols = ['+', '-']

    #Iterate through all games in my_games_clean dictionary
    for index, game_df in my_games_clean.items():

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
            if column == '+':
                GamesSince.loc[game_df[game_df['+/-'] > 0].index, column] = 0
                GamesSince.loc[game_df[game_df['+/-'] <= 0].index, column] += 1
            elif column == '-':
                GamesSince.loc[game_df[game_df['+/-'] < 0].index, column] = 0
                GamesSince.loc[game_df[game_df['+/-'] >= 0].index, column] += 1

    #Save GamesSince
    savePickle(GamesSince, 'dailyGamesSince/dailyGamesSince_{}'.format(myDate))

    print('Finished updating GamesSince for {}'.format(myDate))

def incorporateSpecificDaysStats(date='2000-1-1'):

    #Convert date to datetime
    myDate = pd.to_datetime(date, format='%Y-%m-%d').date()

    #Instantiate my_games_clean
    my_games_clean = pd.read_pickle('dailyGamesClean/dailyGamesClean_{}.pickle'.format(myDate))

    print('Adding {} games to my_df'.format(len(my_games_clean)))

    #Load in the day befores my_df
    my_df = pd.read_pickle('dailyMyDF/dailyMyDF_{}.pickle'.format(myDate - datetime.timedelta(days=1)))

    #Create main df for all day's games
    new_df = pd.concat([game for game in my_games_clean.values()], sort=True)
    new_df = new_df.groupby(new_df.index).sum()

    #Combine my_df and new_df
    my_df = my_df.add(new_df, fill_value=0)

    # Convert columns to int
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        if column in my_df.columns:
            my_df[column] = my_df[column].astype(int)

    savePickle(my_df, 'dailyMyDF/dailyMyDF_{}'.format(myDate))

'--------------- Yesterday Scrape Functions ---------------'

def scrapeYesterdaysURLS():

    """[scrapes all html links for the given date storing them in a piclkle file labeled by day'.
    """
    yesterdaysDate = (pd.to_datetime('today') - datetime.timedelta(days=1)).date()

    daily_html_links = {}

    total_home_teams = []
    total_away_teams = []
    all_game_dates = []

    print('Scraping game links for games on {}'.format(yesterdaysDate))

    # Get the html links for the tables
    my_html_results = getURLS(yesterdaysDate.month, yesterdaysDate.day, yesterdaysDate.year)
    daily_html_links[str(yesterdaysDate)] = my_html_results[0]
    total_home_teams.extend(my_html_results[1])
    total_away_teams.extend(my_html_results[2])
    all_game_dates.extend(my_html_results[3])

    # Pickle the 'daily_html_links' dict using the highest protocol available.
    savePickle(daily_html_links, 'dailyHTMLLinks/dailyHTMLLinks_{}'.format(yesterdaysDate))

    # Flatten list of game htmls
    flat_list_game_links = [item for sublist in list(daily_html_links.values()) for item in sublist]

    #Save home teams, away teams, and game dates in df
    teams_and_dates = pd.DataFrame([total_home_teams, total_away_teams, all_game_dates, flat_list_game_links])
    teams_and_dates = teams_and_dates.transpose()
    savePickle(teams_and_dates, 'dailyTeamsAndDates/dailyTeamsAndDates_{}'.format(yesterdaysDate))

    print('Total game links scraped = {}'.format(len(teams_and_dates)))

def scrapeYesterdaysGames(): 

    yesterdaysDate = (pd.to_datetime('today') - datetime.timedelta(days=1)).date()

    #Create my_games_unclean dict to store scraped games
    dailyGamesUnclean = {}

    yesterdaysGames = pd.read_pickle('dailyTeamsAndDates/dailyTeamsAndDates_{}.pickle'.format(yesterdaysDate))
    number_of_games = len(yesterdaysGames)
    print('Number of games to scrape = {}'.format(number_of_games))

    #Instantiate counter for reporting scrape progress and create % thresholds
    my_count = 0
    threshold_25 = int(number_of_games*0.25)
    threshold_50 = int(number_of_games*0.5)
    threshold_75 = int(number_of_games*0.75)

    # Use  html links to create games' dataframes
    for game in range(number_of_games):
        dailyGamesUnclean[game] = scrapeGame(
            my_url=yesterdaysGames.iloc[game, 3], 
            game_date=yesterdaysGames.iloc[game, 2],
            home_team_name=yesterdaysGames.iloc[game, 0],
            away_team_name=yesterdaysGames.iloc[game, 1])
        my_count += 1
        if my_count == threshold_25:
            print("Scraped 25% of total games")
        elif my_count == threshold_50:
            print("Scraped 50% of total games")
        elif my_count == threshold_75:
            print("Scraped 75% of total games")
    
    # Pickle the 'my_games' dictionary using the highest protocol available.
    savePickle(dailyGamesUnclean, 'dailyGamesUnclean/dailyGamesUnclean_{}'.format(yesterdaysDate))

    print('Number of games scraped = {}'.format(len(dailyGamesUnclean)))

def cleanYesterdaysGames():

    yesterdaysDate = (pd.to_datetime('today') - datetime.timedelta(days=1)).date()

    my_games_unclean = pd.read_pickle('dailyGamesUnclean/dailyGamesUnclean_{}.pickle'.format(yesterdaysDate))
    my_games_clean = {}

    print('Number of games to clean = {}'.format(len(my_games_unclean)))

    for index, game in my_games_unclean.items():
        my_games_clean[index] = cleanGame(game)

    savePickle(my_games_clean, 'dailyGamesClean/dailyGamesClean_{}'.format(yesterdaysDate))

    print('Number of games cleaned  = {}'.format(len(my_games_clean)))

def updateYesterdaysLastTime():

    print("Updating Last Time to reflect new stats' dates")

    yesterdaysDate = (pd.to_datetime('today') - datetime.timedelta(days=1)).date()

    #Load in last_time_df from the previous day, which will be copied and updated
    last_time_df = pd.read_pickle('dailyLastTime/dailyLastTime_{}.pickle'.format(yesterdaysDate - datetime.timedelta(days=1))).copy()

    #Load my_games_clean dictionary
    my_games_clean = pd.read_pickle('dailyGamesClean/dailyGamesClean_{}.pickle'.format(yesterdaysDate))

    #Set columns to iterate through
    cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    #Also add in last times the player was + or -
    pmCols = ['+', '-']

    #Iterate through all games in my_games_clean dictionary
    for index, game_df in my_games_clean.items():

        #Create the new index, which is a union of the main one and the one from the specific game
        new_index = last_time_df.index.union(game_df.index)
        #Implement the new index, filling in empty values with the date '2000/10/4' (start of '00 season)
        last_time_df = last_time_df.reindex(new_index, fill_value=datetime.date(2000,10,3))
        #Collect the date of the game
        game_date = game_df['Date'].mode()

        #Iterate through columns to update date for goals, assists, etc.
        for column in cols:
            last_time_df.loc[game_df[game_df[column] > 0].index, column] = game_date[0]

        #Set last game date to current game's date
        last_time_df.loc[game_df.index, 'Last Game Date'] = game_date[0]

        #Iterate through columns to edit +/- columns
        for column in pmCols:
            if column == '+':
                last_time_df.loc[game_df[game_df['+/-'] > 0].index, column] = game_date[0]
            elif column == '-':
                last_time_df.loc[game_df[game_df['+/-'] < 0].index, column] = game_date[0]

    #Save only the date, not the time
    for column in last_time_df.columns:
        try:
            last_time_df[column] = last_time_df[column].dt.date
        except AttributeError:
            pass

    #Save last_time_df
    savePickle(last_time_df, 'dailyLastTime/dailyLastTime_{}'.format(yesterdaysDate))

def updateYesterdaysGamesSince():

    yesterdaysDate = (pd.to_datetime('today') - datetime.timedelta(days=1)).date()

    print("Updating GamesSince to reflect new stats' timelines for yerterday, {}".format(yesterdaysDate))

    #Load in GamesSince from the previous day, which will be copied and updated
    GamesSince = pd.read_pickle('dailyGamesSince/dailyGamesSince_{}.pickle'.format(yesterdaysDate - datetime.timedelta(days=1))).copy()

    #Load my_games_clean dictionary
    my_games_clean = pd.read_pickle('dailyGamesClean/dailyGamesClean_{}.pickle'.format(yesterdaysDate))
    
    #Set columns to iterate through
    cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    #Also add in last times the player was + or -
    pmCols = ['+', '-']

    #Iterate through all games in my_games_clean dictionary
    for index, game_df in my_games_clean.items():

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
            if column == '+':
                GamesSince.loc[game_df[game_df['+/-'] > 0].index, column] = 0
                GamesSince.loc[game_df[game_df['+/-'] <= 0].index, column] += 1
            elif column == '-':
                GamesSince.loc[game_df[game_df['+/-'] < 0].index, column] = 0
                GamesSince.loc[game_df[game_df['+/-'] >= 0].index, column] += 1

    #Save GamesSince
    savePickle(GamesSince, 'dailyGamesSince/dailyGamesSince_{}'.format(yesterdaysDate))

    print('Finished updating GamesSince for yesterday, {}'.format(yesterdaysDate))

def incorporateYesterdaysStats():

    yesterdaysDate = (pd.to_datetime('today') - datetime.timedelta(days=1)).date()

    #Instantiate my_games_clean
    my_games_clean = pd.read_pickle('dailyGamesClean/dailyGamesClean_{}.pickle'.format(yesterdaysDate))

    print('Adding {} games to my_df'.format(len(my_games_clean)))

    #Load in the day befores my_df
    my_df = pd.read_pickle('dailyMyDF/dailyMyDF_{}.pickle'.format(yesterdaysDate - datetime.timedelta(days=1)))

    #Create main df for all day's games
    new_df = pd.concat([game for game in my_games_clean.values()], sort=True)
    new_df = new_df.groupby(new_df.index).sum()

    #Combine my_df and new_df
    my_df = my_df.add(new_df, fill_value=0)

    # Convert columns to int
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        if column in my_df.columns:
            my_df[column] = my_df[column].astype(int)

    savePickle(my_df, 'dailyMyDF/dailyMyDF_{}'.format(yesterdaysDate))

'--------------- Multi-Game Functions ---------------'

def scrapeURLRange(start_date, end_date):

    """[scrapes all html links for each each between the given dates, exclusive of the end date, storing them in the file all_html_links.pickle'.
    """

    start_date = pd.to_datetime(start_date, format='%Y/%m/%d')
    end_date = pd.to_datetime(end_date, format='%Y/%m/%d')
    all_html_links = {}

    total_home_teams = []
    total_away_teams = []
    all_game_dates = []

    print('Scraping game links between dates {} and {}'.format(start_date.date(), end_date.date()))

    # Get the html links for the tables
    while start_date != end_date:
        my_html_results = getURLS(start_date.month, start_date.day, start_date.year)
        all_html_links[str(start_date)] = my_html_results[0]
        total_home_teams.extend(my_html_results[1])
        total_away_teams.extend(my_html_results[2])
        all_game_dates.extend(my_html_results[3])
        start_date += datetime.timedelta(days=1)
        time.sleep(1)

    # Pickle the 'all_html_links' dict using the highest protocol available.
    savePickle(all_html_links, 'all_html_links')

    # Flatten list of game htmls
    flat_list_game_links = [item for sublist in list(all_html_links.values()) for item in sublist]

    #Save home teams, away teams, and game dates in df
    teams_and_dates = pd.DataFrame([total_home_teams, total_away_teams, all_game_dates, flat_list_game_links])
    savePickle(teams_and_dates, 'teams_and_dates')

    print('Total game links scraped = {}'.format(len(teams_and_dates.columns)))

def scrapeYearsURLs(end_year):
    
    """Scrape all html links for games across an entire NHL season. 
    This uses the table available at 
    'https://www.hockey-reference.com/leagues/NHL_YYYY_games.html', 
    where YYYY is the year"""

    print('Scraping all urls for games in season {}-{}'.format(end_year-1, end_year))

    #General url
    url = 'https://www.hockey-reference.com/leagues/NHL_{}_games.html'.format(end_year)

    #Process the html
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'lxml')
    table = soup.find('table', id='games') 

    #Select the first resulting table, namely that of the Regular Season stats. Table 2 is the playoffs stats.
    seasonSummary = pd.read_html(url)[0]
    seasonSummary = seasonSummary[['Date', 'Home', 'Visitor']]
    my_urls = pd.Series([[th.a['href'] if th.find('a') else ''.join(th.stripped_strings) for th in row.find_all('th')] for row in table.find_all('tr')][1:])
    my_urls = [item for sublist in my_urls for item in sublist]
    seasonSummary.loc[:, 'url'] = my_urls
    seasonSummary = seasonSummary[seasonSummary['url'].str.contains('boxscore')]
    seasonSummary['url'] = 'https://www.hockey-reference.com' + seasonSummary['url']

    #Save resulting file
    savePickle(seasonSummary, 'seasonSummary', end_year-1, end_year)

    print('Finished scraping game urls')

def scrapeAvailableGames(end_year=None):

    """[scrapes game data in file 'teams_and_dates.pickle' incorporating the resulting dfs into the file 'my_games_unclean.pickle']
    If end_year is False, scraping in range and will return a df with columns representing each game
    If end_year is True, it will scrape a full year
    """

    #Create my_games_unclean dict to store scraped games
    my_games_unclean = {}

    if end_year is None:

        #Load in required data
        teams_and_dates = pd.read_pickle('teams_and_dates.pickle')
        number_of_games = len(teams_and_dates.columns)
        print('Number of games to scrape = {}'.format(number_of_games))

        #Instantiate counter for reporting scrape progress and create % thresholds
        my_count = 0
        threshold_25 = int(number_of_games*0.25)
        threshold_50 = int(number_of_games*0.5)
        threshold_75 = int(number_of_games*0.75)

        # Use  html links to create games' dataframes
        for game in range(len(teams_and_dates.columns)):
            my_games_unclean[game] = scrapeGame(
                my_url=teams_and_dates.iloc[3, game], 
                game_date=teams_and_dates.iloc[2, game],
                home_team_name=teams_and_dates.iloc[0, game],
                away_team_name=teams_and_dates.iloc[1, game])
            time.sleep(1)
            my_count += 1
            if my_count == threshold_25:
                print("Scraped 25% of total games")
            elif my_count == threshold_50:
                print("Scraped 50% of total games")
            elif my_count == threshold_75:
                print("Scraped 75% of total games")

        # Pickle the 'my_games' dictionary using the highest protocol available.
        savePickle(my_games_unclean, 'my_games_unclean')

    else:
        seasonSummary = pd.read_pickle('seasonSummary_{}_{}.pickle'.format(end_year-1, end_year))
        number_of_games = len(seasonSummary)
        print('Number of games to scrape = {}'.format(number_of_games))

        #Instantiate counter for reporting scrape progress and create % thresholds
        my_count = 0
        threshold_25 = int(number_of_games*0.25)
        threshold_50 = int(number_of_games*0.5)
        threshold_75 = int(number_of_games*0.75)

        # Use  html links to create games' dataframes
        for game in range(len(seasonSummary)):
            my_games_unclean[game] = scrapeGame(
                my_url=seasonSummary.iloc[game, 3], 
                game_date=seasonSummary.iloc[game, 0],
                home_team_name=seasonSummary.iloc[game, 1],
                away_team_name=seasonSummary.iloc[game, 2])
            time.sleep(1)
            my_count += 1
            if my_count == threshold_25:
                print("Scraped 25% of total games")
            elif my_count == threshold_50:
                print("Scraped 50% of total games")
            elif my_count == threshold_75:
                print("Scraped 75% of total games")
        
        # Pickle the 'my_games' dictionary using the highest protocol available.
        savePickle(my_games_unclean, 'my_games_unclean', end_year-1, end_year)

    print('Number of games scraped = {}'.format(len(my_games_unclean)))

def cleanUncleanGames(end_year):

    """[Cleans the data present in each game of my_games_unclean dictionary]
    """

    #Create variable start_year
    start_year = end_year - 1

    my_games_unclean = pd.read_pickle('my_games_unclean_{}_{}.pickle'.format(start_year, end_year))
    my_games_clean = {}

    print('Number of games to clean = {}'.format(len(my_games_unclean)))

    for index, game in my_games_unclean.items():
        my_games_clean[index] = cleanGame(game)

    savePickle(my_games_clean, 'my_games_clean', start_year, end_year)

    print('Number of games cleaned  = {}'.format(len(my_games_clean)))

def updateLastTime(end_year):

    """Update df containing the dates of the last time each player scored, hit, etc"""

    print("Updating Last Time to reflect new stats' dates")

    #Create variable start_year
    start_year = end_year - 1

    #Load in last_time_df from the PREVIOUS season, which will be copied and updated
    last_time_df = pd.read_pickle('last_time_df_{}_{}.pickle'.format(start_year-1, end_year-1)).copy()

    #Load my_games_clean dictionary
    my_games_clean = pd.read_pickle('my_games_clean_{}_{}.pickle'.format(start_year, end_year))

    #Set columns to iterate through
    cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    #Also add in last times the player was + or -
    pmCols = ['+', '-']

    #Iterate through all games in my_games_clean dictionary
    for index, game_df in my_games_clean.items():

        #Create the new index, which is a union of the main one and the one from the specific game
        new_index = last_time_df.index.union(game_df.index)
        #Implement the new index, filling in empty values with the date '2000/10/4' (start of '00 season)
        last_time_df = last_time_df.reindex(new_index, fill_value=datetime.date(2000,10,3))
        #Collect the date of the game
        game_date = game_df['Date'].mode()

        #Iterate through columns to update date for goals, assists, etc.
        for column in cols:
            last_time_df.loc[game_df[game_df[column] > 0].index, column] = game_date[0]

        #Set last game date to current game's date
        last_time_df.loc[game_df.index, 'Last Game Date'] = game_date[0]

        #Iterate through columns to edit +/- columns
        for column in pmCols:
            if column == '+':
                last_time_df.loc[game_df[game_df['+/-'] > 0].index, column] = game_date[0]
            elif column == '-':
                last_time_df.loc[game_df[game_df['+/-'] < 0].index, column] = game_date[0]

    #Save only the date, not the time
    for column in last_time_df.columns:
        try:
            last_time_df[column] = last_time_df[column].dt.date
        except AttributeError:
            pass

    #Save last_time_df
    savePickle(last_time_df, 'last_time_df', start_year, end_year)

def updateGamesSince(end_year):
    """A function to update the DataFrame that notes the number of games since a player has scored, gotten an assist, etc."""

    #Create variable start_year
    start_year = end_year - 1

    print("Updating GamesSince to reflect new stats' timelines for the season spanning {} to {}".format(start_year, end_year))

    #Load in GamesSince from the PREVIOUS season, which will be copied and updated
    GamesSince = pd.read_pickle('GamesSince_{}_{}.pickle'.format(start_year-1, end_year-1)).copy()

    #Load my_games_clean dictionary
    my_games_clean = pd.read_pickle('my_games_clean_{}_{}.pickle'.format(start_year, end_year))

    #Set columns to iterate through
    cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    #Also add in last times the player was + or -
    pmCols = ['+', '-']

    #Iterate through all games in my_games_clean dictionary
    for index, game_df in my_games_clean.items():

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
            if column == '+':
                GamesSince.loc[game_df[game_df['+/-'] > 0].index, column] = 0
                GamesSince.loc[game_df[game_df['+/-'] <= 0].index, column] += 1
            elif column == '-':
                GamesSince.loc[game_df[game_df['+/-'] < 0].index, column] = 0
                GamesSince.loc[game_df[game_df['+/-'] >= 0].index, column] += 1

    #Save GamesSince
    savePickle(GamesSince, 'GamesSince', start_year, end_year)

    print('Finished updating GamesSince for the year {} through {}'.format(start_year, end_year))

def incorporateNewStats(end_year):

    """[updates my_df]
    Returns:
        [none] -- [just updates my_df]
    """

    #Create variable start_year
    start_year = end_year - 1

    #Instantiate my_games_clean
    my_games_clean = pd.read_pickle('my_games_clean_{}_{}.pickle'.format(start_year, end_year))

    print('Adding {} games to my_df'.format(len(my_games_clean)))

    #Create main df for all day's games
    my_df = pd.concat([game for game in my_games_clean.values()])

    #Combine stats for each player, between games
    my_df = my_df.groupby(my_df.index).sum()

    # Convert columns to int
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        if column in my_df.columns:
            my_df[column] = my_df[column].astype(int)

    savePickle(my_df, 'my_df', start_year, end_year)

'--------------- Aggregate Scraping, Updating Functions ---------------'

def scrapeYesterday():
    """ Scrape, clean, incorporate yesterday's stats """
    #Check if yesterdays data was already scraped, by checking for one of the indicative files (dailyGamesClean)
    yesterdaysDate = pd.to_datetime('today').date() - datetime.timedelta(days=1)
    filename = 'dailyGamesClean/dailyGamesClean_{}.pickle'.format(yesterdaysDate)
    
    if os.path.isfile(filename):
        print('\nYesterday was already scraped -- skipping scrape\n')
    else:
        print('Scraping yesterdays data')
        scrapeYesterdaysURLS()
        scrapeYesterdaysGames()
        cleanYesterdaysGames()
        updateYesterdaysLastTime()
        updateYesterdaysGamesSince()
        incorporateYesterdaysStats()

    #Show recent performers!!
    showRecentPerformers()

def scrapeSpecificDay(day='2018-11-26'):

    """ Scrape, clean, incorporate specific day's stats """

    day = pd.to_datetime(day, format='%Y-%m-%d')
    myGames = scrapeSpecificDaysURLS(day)
    if myGames == 'Games Found':
        scrapeSpecificDaysGames(day)
        cleanSpecificDaysGames(day)
        updateSpecificDaysLastTime(day)
        updateSpecificDaysSince(day)
        incorporateSpecificDaysStats(day)
    else:
        myDate = pd.to_datetime(day, format='%Y-%m-%d').date()
        #Save new version of LastTime
        myLastTime = pd.read_pickle('dailyLastTime/dailyLastTime_{}.pickle'.format(myDate - datetime.timedelta(days=1)))
        savePickle(myLastTime, 'dailyLastTime/dailyLastTime_{}'.format(myDate))
        #Save new version of GamesSince
        myGamesSince = pd.read_pickle('dailyGamesSince/dailyGamesSince_{}.pickle'.format(myDate - datetime.timedelta(days=1)))
        savePickle(myGamesSince, 'dailyGamesSince/dailyGamesSince_{}'.format(myDate))
        #Save new version of my_df
        my_df = pd.read_pickle('dailyMyDF/dailyMyDF_{}.pickle'.format(myDate - datetime.timedelta(days=1)))
        savePickle(my_df, 'dailyMyDF/dailyMyDF_{}'.format(myDate))

def scrapeToToday():
    """Scrape games day-by-day, up to current day
    Accomodates previously-scraped days. Automatically finds last-scraped day"""

    #Find last scraped day; indicated by presence of that day's myDF
    myDate = pd.to_datetime('today').date()
    today = pd.to_datetime('today').date()
    while True:
        try:
            myDF = pd.read_pickle('dailyMyDF/dailyMyDF_{}.pickle'.format(myDate))
            break
        except:
            myDate -= datetime.timedelta(days=1)

    #Increase date to first unscraped day (next day)
    myDate += datetime.timedelta(days=1)

    #Iteratively scrape each day
    while myDate != today:
        scrapeSpecificDay(day=str(myDate))
        myDate += datetime.timedelta(days=1)

def scrapeYear(end_year):
    """Function to scrape, clean, save, and incorporate data from the given 
    NHL season. The year provided is the end_year of the season, such as 
    2006 for the 2005-2006 season"""

    #Update stats between these dates
    scrapeYearsURLs(end_year)
    scrapeAvailableGames(end_year)
    cleanUncleanGames(end_year)
    updateLastTime(end_year)
    incorporateNewStats(end_year)

    #Report major stats from my_df for this year
    my_df = pd.read_pickle('my_df_{}_{}.pickle'.format(end_year-1, end_year))
    my_df_QC(my_df)

def scrapeToNow(start_date='2000/12/31'):
    """Scrape individual days from the start date to yesterday"""
    myDate = pd.to_datetime(start_date, format='%Y-%m-%d').date()
    todaysDate  = pd.to_datetime('today').date()

    while myDate != todaysDate:
        scrapeSpecificDay(str(myDate))
        myDate += datetime.timedelta(days=1)

'--------------- Data-Reporting Functions ---------------'

def openLatestMyDF():
    myDate = pd.to_datetime('today').date()
    while True:
        try:
            myDF = pd.read_pickle('dailyMyDF/dailyMyDF_{}.pickle'.format(myDate))
            break
        except:
            myDate -= datetime.timedelta(days=1)
    return myDF

def openLatestLastTime():
    myDate = pd.to_datetime('today').date()
    while True:
        try:
            lastTime = pd.read_pickle('dailyLastTime/dailyLastTime_{}.pickle'.format(myDate))
            break
        except:
            myDate -= datetime.timedelta(days=1)
    return lastTime

def openLatestGamesSince():
    myDate = pd.to_datetime('today').date()
    while True:
        try:
            gamesSince = pd.read_pickle('dailyGamesSince/dailyGamesSince_{}.pickle'.format(myDate))
            break
        except:
            myDate -= datetime.timedelta(days=1)
    return gamesSince

'--------------- Helper Functions ---------------'

def savePickle(variable, variable_name, start_year=None, end_year=None):
    """Save the given variable as a pickle file, with the filename ending with '.pickle'"""
    if start_year and end_year:
        filename = variable_name + '_{}_{}'.format(start_year, end_year) + '.pickle'
    else:
        filename = variable_name + '.pickle'
    with open(filename, 'wb') as f:
        pickle.dump(variable, f, pickle.HIGHEST_PROTOCOL)

def new_last_time_df():
    """ Create a new last_time_df file """
    return pd.DataFrame(columns=['G', 'A', 'PTS', '+', '-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Last Game Date'])

def my_df_QC(my_df):
    """ Run random QC tests on my_df """
    print('Len my_df:', len(my_df))
    print('Max goals:', my_df['G'].max())
    print('Max goalscorer:', my_df[my_df['G'] == my_df['G'].max()].index[0])
    print('Max TOI:  ', my_df['TOI'].max())
    print('Max TOI Player:', my_df[my_df['TOI'] == my_df['TOI'].max()].index[0])

def restartAll():
    """A function to create a brand new statistical workspace"""
    user_input = input('Are you sure you want to clear all previous data? (y/n)    ')
    if user_input.lower() == 'y':

        #Create new, empty variables (dfs, etc)
        last_time_df = new_last_time_df()
        my_games_clean = {}
        all_time_clean_games = {}

        #Save all new variables
        savePickle(last_time_df, 'last_time_df')
        savePickle(my_games_clean, 'my_games_clean')
        savePickle(all_time_clean_games, 'all_time_clean_games')

    else:
        pass

def showRecentPerformers():
    """A function to return summarizing statistics focusing on GamesSince for current players"""
    #Select yesterday -- even if no games were played then, the update functions will accomodate and create it accurate dataframes
    myDate = pd.to_datetime('today').date() - datetime.timedelta(days=1)

    #Load in LastTime and GamesSince dataframes
    lastTime = pd.read_pickle('dailyLastTime/dailyLastTime_{}.pickle'.format(myDate))
    gamesSince = pd.read_pickle('dailyGamesSince/dailyGamesSince_{}.pickle'.format(myDate))

    #Select only players who've played this year
    currentPlayers = lastTime[lastTime['Last Game Date'] > pd.to_datetime('2018-10-1', format='%Y-%m-%d').date()]
    # print(min(currentPlayers['Last Game Date']))
    currentPlayersIndex = currentPlayers.index
    currentPlayersGamesSince = gamesSince.reindex(currentPlayersIndex)

    #Create a column 'Average', that averages all stats
    myCols = ['G', 'A', '+', 'EV', 'PP', 'SH', 'GW', 'S']
    currentPlayersGamesSince['Average'] = currentPlayersGamesSince[myCols].mean(axis=1).round(2)

    #Select only players who've played enough career games to validate low averages being good
    #(An average of 2 days since scoring, assisting, etc. is good, but only if the player has played more than 2 games!)
    currentPlayersGamesSince = currentPlayersGamesSince[currentPlayersGamesSince['Total Recorded Games'] >= 25]

    print('\nLongest droughts\n')

    #Sort by different category to show underperformers
    for column in currentPlayersGamesSince.columns:
        for player in currentPlayersGamesSince.sort_values(column, ascending=False).head(3).index:
            print('{}\t{}\t{}'.format(column, player, currentPlayersGamesSince.loc[player, column]))

'--------------- Call To Provided Functions ---------------'

if __name__ == '__main__':
    scrapeToToday()

'----------------------------------------------------------'

# a = openLatestMyDF()
# b = openLatestLastTime()
# c = openLatestGamesSince()
