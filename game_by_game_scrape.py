# Scrape the website https://www.hockey-reference.com for game-by-game stats

import pandas as pd
import pickle
import requests
from bs4 import BeautifulSoup
from My_Classes import LengthException
import datetime
import time


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
    savePickle(all_html_links, 'all_html_links.pickle')

    # Flatten list of game htmls
    flat_list_game_links = [item for sublist in list(all_html_links.values()) for item in sublist]

    #Save home teams, away teams, and game dates in df
    teams_and_dates = pd.DataFrame([total_home_teams, total_away_teams, all_game_dates, flat_list_game_links])
    savePickle(teams_and_dates, 'teams_and_dates.pickle')

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

#Scrape data only between these days, start-inclusive and end-exclusive
def updateDF(df, startDate='2000/10/4', endDate='2001/4/9'):
    """ Run all prescribed functions on my_df, pulling html links, game data, then incorporating it to the file 'my_df.pickle' """
    scrapeURLRange(startDate, endDate)
    scrapeAvailableGames()
    cleanUncleanGames()
    updateLastTime()
    incorporateNewStats(df)

# function to run above functions to scrape, clean, and incorporate data
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

'--------------- Helper Functions ---------------'

#Generic save pickle file helper functions
def savePickle(variable, variable_name, start_year=None, end_year=None):
    """Save the given variable as a pickle file, with the filename ending with '.pickle'"""
    if start_year and end_year:
        filename = variable_name + '_{}_{}'.format(start_year, end_year) + '.pickle'
    else:
        filename = variable_name + '.pickle'
    with open(filename, 'wb') as f:
        pickle.dump(variable, f, pickle.HIGHEST_PROTOCOL)

# Create new last_time_df
def new_last_time_df():
    """ Create a new last_time_df file """
    return pd.DataFrame(columns=['G', 'A', 'PTS', '+', '-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Last Game Date'])

# Print QC information
def my_df_QC(my_df):
    """ Run random QC tests on my_df """
    print('Len my_df:', len(my_df))
    print('Max goals:', my_df['G'].max())
    print('Max goalscorer:', my_df[my_df['G'] == my_df['G'].max()].index[0])
    print('Max TOI:  ', my_df['TOI'].max())
    print('Max TOI Player:', my_df[my_df['TOI'] == my_df['TOI'].max()].index[0])

#Create new, blank variables
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

'--------------- Call To Provided Functions ---------------'

# if __name__ == '__main__':
#     scrapeYear(2015)

'----------------------------------------------------------'