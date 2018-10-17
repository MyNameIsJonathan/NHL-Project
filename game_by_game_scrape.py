# Scrape the website https://www.hockey-reference.com for game-by-game stats

import pandas as pd
import pickle
import requests
from bs4 import BeautifulSoup
from My_Classes import LengthException
import datetime
import time


'--------------- Single-Game-Specific Functions ---------------'

def getHTMLLinks(month, day, year):

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

    """[Function to pull stats from a single game, given the url (attained through getHTMLLinks), the date (also from getHTMLLinks), home and away teams]
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
    cols_to_drop = ['S%', 'EV.2', 'PP.2', 'SH.2', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17']
    df = df.drop([column for column in cols_to_drop if column in df.columns], axis=1)

    # Rename columns for better readability
    df = df.rename(columns = {'EV.1':'EV', 'PP.1':'PP', 'SH.1':'SH', 'SHFT':'Shifts'})

    #Fill NaN values to convert to int
    df = df.fillna(0)

    #Get int of minutes on ice from string "mm:ss"
    df['TOI'] = df['TOI'].str.split(':')
    df['TOI'] = df['TOI'].apply(lambda x: int(x[0]) + int(x[1])/60)
    df['TOI'] = df['TOI'].round(2)
    
    return df

'--------------- Multi-Game Functions ---------------'

def scrapeHTMLRange(start_date, end_date):

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
        my_html_results = getHTMLLinks(start_date.month, start_date.day, start_date.year)
        all_html_links[str(start_date)] = my_html_results[0]
        total_home_teams.extend(my_html_results[1])
        total_away_teams.extend(my_html_results[2])
        all_game_dates.extend(my_html_results[3])
        start_date += datetime.timedelta(days=1)
        time.sleep(1)

    # Pickle the 'all_html_links' dict using the highest protocol available.
    with open('all_html_links.pickle', 'wb') as f:
        pickle.dump(all_html_links, f, pickle.HIGHEST_PROTOCOL)

    # Flatten list of game htmls
    flat_list_game_links = [item for sublist in list(all_html_links.values()) for item in sublist]

    #Save home teams, away teams, and game dates in df
    teams_and_dates = pd.DataFrame([total_home_teams, total_away_teams, all_game_dates, flat_list_game_links])
    with open('teams_and_dates.pickle', 'wb') as f:
        pickle.dump(teams_and_dates, f, pickle.HIGHEST_PROTOCOL)

    print('Total game links scraped = {}'.format(len(teams_and_dates.columns)))

def scrapeAvailableGames():

    """[scrapes game data in file 'teams_and_dates.pickle' incorporating the resulting dfs into the file 'my_games_unclean.pickle']
    """

    #Load in required data
    teams_and_dates = pd.read_pickle('teams_and_dates.pickle')
    number_of_games = len(teams_and_dates.columns)
    print('Number of games to scrape = {}'.format(number_of_games))

    #Create my_games_unclean dict to store scraped games
    my_games_unclean = {}

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
        my_progress = len(teams_and_dates.columns)/my_count
        if my_progress == threshold_25:
            print("Scraped 25% of total games")
        elif my_progress == threshold_50:
            print("Scraped 50% of total games")
        elif my_progress == threshold_75:
            print("Scraped 75% of total games")

    # Pickle the 'my_games' dictionary using the highest protocol available.
    with open('my_games_unclean.pickle', 'wb') as f:
        pickle.dump(my_games_unclean, f, pickle.HIGHEST_PROTOCOL)

    print('Number of games scraped = {}'.format(len(my_games_unclean)))

def cleanUncleanGames():

    """[Cleans the data present in each game of my_games_unclean dictionary]
    """

    my_games_unclean = pd.read_pickle('my_games_unclean.pickle')
    my_games_clean = {}

    print('Number of games to clean = {}'.format(len(my_games_unclean)))

    for index, game in my_games_unclean.items():
        my_games_clean[index] = cleanGame(game)

    with open('my_games_clean.pickle', 'wb') as f:
        pickle.dump(my_games_clean, f, pickle.HIGHEST_PROTOCOL)

    print('Number of games cleaned  = {}'.format(len(my_games_clean)))

def updateLastTime():

    """Update df containing the dates of the last time each player scored, hit, etc"""

    #Load in last_time_df
    last_time_df = open_last_time_df()

    #Load my_games_clean dictionary
    my_games_clean = open_my_games_clean()

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
    save_last_time_df(last_time_df)

def incorporateNewStats(my_df):

    """[updates my_df]
    Returns:
        [none] -- [just updates my_df]
    """

    my_games_clean = pd.read_pickle('my_games_clean.pickle')

    print('Adding {} games to my_df'.format(len(my_games_clean)))

    # Create master df, initialized with first df in my_games dictionary &
    # Iterate through games' dfs, merging them into the main df, then adding their values to the main df (Ex: Adding Goal totals)
    columns_to_add = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Shifts', 'TOI']

    #Keep only these columns -- removes 'Date' column, which is in last_time_df
    my_df = my_df[columns_to_add]

    #Create main df for all day's games
    new_df = pd.concat([game for game in my_games_clean.values()])

    #Combine stats for each player, between games
    new_df = new_df.groupby(new_df.index).sum()

    #Save new_df
    with open('new_df.pickle', 'wb') as f:
        pickle.dump(new_df, f, pickle.HIGHEST_PROTOCOL)

    #Add this day's games df to my_df
    my_df = my_df.add(new_df[columns_to_add], fill_value=0) 

    # Convert columns to int
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        if column in my_df.columns:
            my_df[column] = my_df[column].astype(int)

    save_my_df(my_df)

    # Use unclean games to get min and max dates 
    my_games_unclean = open_my_games_unclean()
    unclean_df = pd.concat([game for game in my_games_unclean.values()])
    my_key = 'Dates: {} to {}'.format(unclean_df['Date'].min(), unclean_df['Date'].max())

    # Move games from my_games_clean dict to all_time_clean_games
    all_time_clean_games = open_all_time_clean_games()
    all_time_clean_games[my_key] = list(my_games_clean.values())
    if len(all_time_clean_games[my_key]) == len(my_games_clean):
        my_games_clean = {}
        save_my_games_clean(my_games_clean)
        save_all_time_clean_games(all_time_clean_games)
    else:
        raise LengthException('Number of clean games does not equal length of preserved games val')

    print('My_games_clean now empty:', len(my_games_clean) == 0)
    print('Games added to all_time_clean_games:', len(all_time_clean_games[my_key]))

'--------------- Aggregate Scraping, Updating Functions ---------------'

#Scrape data only between these days, start-inclusive and end-exclusive
def updateDF(df, startDate='2000/10/4', endDate='2001/4/9'):
    """ Run all prescribed functions on my_df, pulling html links, game data, then incorporating it to the file 'my_df.pickle' """
    scrapeHTMLRange(startDate, endDate)
    scrapeAvailableGames()
    cleanUncleanGames()
    updateLastTime()
    incorporateNewStats(df)

# function to run above functions to scrape, clean, and incorporate data
def scrapeYear(end_year):
    """Function to scrape, clean, save, and incorporate data from the given 
    NHL season. The year provided is the end_year of the season, such as 
    2006 for the 2005-2006 season"""

    #Get start_year
    start_year = end_year - 1

    #Reset my_df
    yearlyRestart()

    #Instantiate my_df
    my_df = open_my_df()

    #Get start and end dates of the regular season from hockey-reference.com
    my_file = 'https://www.hockey-reference.com/leagues/NHL_{}_games.html'.format(end_year)
    my_years_df = pd.read_html(my_file)[0]
    start_date = my_years_df.iloc[0, 0]
    end_date = str(pd.to_datetime(my_years_df.iloc[-1, 0]).date() + datetime.timedelta(days=1))
    del my_years_df

    #Update my_df between these dates
    scrapeHTMLRange(start_date, end_date)
    all_html_links = open_all_html_links() #open all_html_links for saving
    save_yearly_all_html_links(all_html_links, start_year, end_year) #Save all_hml_links with years in the resulting filename
    scrapeAvailableGames()
    my_games_unclean = open_my_games_unclean() #Open my_games_unclean for saving
    save_yearly_my_games_unclean(my_games_unclean, start_year, end_year) #Save my_games_unclean with years in the resulting filename
    cleanUncleanGames()
    my_games_clean = open_my_games_clean() #Load my_games_clean, for saving
    save_yearly_my_games_clean(my_games_clean, start_year, end_year) #Save this year's my_games_clean with years in the resulting filename
    updateLastTime()
    #Checkpoint-save last_time_df for each year, in case it is needed later
    last_time_df = open_last_time_df()
    save_yearly_last_time_df(last_time_df, start_year, end_year)
    incorporateNewStats(my_df)

    #Save changes to my_df, specifying the year
    save_yearly_total_my_df(my_df, years='{}_{}'.format(start_year, end_year))

    #Report major stats from my_df for this year
    my_df = open_my_df()
    top_goal_scorer = my_df[my_df['G'] == my_df['G'].max()].index[0]
    top_assist_scorer = my_df[my_df['A'] == my_df['A'].max()].index[0]
    top_PTS = my_df[my_df['PTS'] == my_df['PTS'].max()].index[0]
    top_pm = my_df[my_df['+/-'] == my_df['+/-'].max()].index[0]
    print("  Top Goals: {}, {}".format(top_goal_scorer, my_df.loc[top_goal_scorer, 'G']))
    print("Top Assists: {}, {}".format(top_assist_scorer, my_df.loc[top_assist_scorer, 'A']))
    print("    Top PTS: {}, {}".format(top_PTS, my_df.loc[top_PTS, 'PTS']))
    print("    Top +/-: {}, {}".format(top_pm, my_df.loc[top_pm, '+/-']))

'--------------- Helper Functions ---------------'

# Create a new, empty my_df
def new_my_df():
    """ Create a new, empty my_df """
    return pd.DataFrame(columns=['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Shifts', 'TOI', 'Team', 'Date'])

#Save my_df as a pickle file
def save_my_df(my_df):
    """ Save my_df as a pickle file """
    with open('my_df.pickle', 'wb') as f:
        pickle.dump(my_df, f, pickle.HIGHEST_PROTOCOL)

# open my_df
def open_my_df():
    """ Open the pickle file 'my_stats_df.pickle' """
    return pd.read_pickle('my_df.pickle')

#Save a year's my_df
def save_yearly_total_my_df(my_df, years='1999_2000'):
    """ Save my_df that contains a full year's stats as a pickle file """
    my_filename = "my_df_{}.pickle".format(years)
    with open(my_filename, 'wb') as f:
        pickle.dump(my_df, f, pickle.HIGHEST_PROTOCOL)

#Open my_df from a specific year
def open_yearly_my_df(years='1999_2000'):
    """ Open the pickle file for a year's stats """
    my_filename = "my_df_{}.pickle".format(years)
    return pd.read_pickle(my_filename)

# Create new last_time_df
def create_new_last_time_df():
    """ Create a new last_time_df file """
    return pd.DataFrame(columns=['G', 'A', 'PTS', '+', '-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Last Game Date'])

# Save last_time_df as pickle file
def save_last_time_df(last_time_df):
    """ Save last_time_df as a pickle file """
    with open('last_time_df.pickle', 'wb') as f:
        pickle.dump(last_time_df, f, pickle.HIGHEST_PROTOCOL)

# Open last_time_df pickle file
def open_last_time_df():
    """ Open the pickle file 'last_time_df.pickle' """
    return pd.read_pickle('last_time_df.pickle')

#Save checkpoint of last_time_df for each year, in case it is needed for troubleshooting
def save_yearly_last_time_df(last_time_df, start_year, end_year):
    my_filename = 'last_time_df_{}_{}.pickle'.format(start_year, end_year)
    with open(my_filename, 'wb') as f:
        pickle.dump(last_time_df, f, pickle.HIGHEST_PROTOCOL)

# Open my_games_unclean
def open_my_games_unclean():
    """ Open the pickle file 'my_games_unclean.pickle' """
    return pd.read_pickle('my_games_unclean.pickle')

#Save my_games_unclean for each year
def save_yearly_my_games_unclean(my_games_unclean, start_year, end_year):
    my_filename = 'my_games_unclean_{}_{}.pickle'.format(start_year, end_year)
    with open(my_filename, 'wb') as f:
        pickle.dump(my_games_unclean, f, pickle.HIGHEST_PROTOCOL)

# Open my_games_clean
def open_my_games_clean():
    """ Open the pickle file 'my_games_clean.pickle' """
    return pd.read_pickle('my_games_clean.pickle')

# Save my_games_clean
def save_my_games_clean(my_games_clean):
    with open('my_games_clean.pickle', 'wb') as f:
        pickle.dump(my_games_clean, f, pickle.HIGHEST_PROTOCOL)

#Save clean games from each year, in case that year's games are needed later 
def save_yearly_my_games_clean(my_games_clean, start_year, end_year):
    my_filename = 'my_games_clean_{}_{}.pickle'.format(start_year, end_year)
    with open(my_filename, 'wb') as f:
        pickle.dump(my_games_clean, f, pickle.HIGHEST_PROTOCOL)

# Save all_time_clean_games dictionary
def save_all_time_clean_games(all_time_clean_games):
    with open('all_time_clean_games.pickle', 'wb') as f:
        pickle.dump(all_time_clean_games, f, pickle.HIGHEST_PROTOCOL)

# Open all_time_clean_games dictionary
def open_all_time_clean_games():
    """ Open the pickle file 'all_time_clean_games.pickle' """
    return pd.read_pickle('all_time_clean_games.pickle')

#Save yearly all_html_links
def save_yearly_all_html_links(all_html_links, start_year, end_year):
    my_filename = 'all_html_links_{}_{}.pickle'.format(start_year, end_year)
    with open(my_filename, 'wb') as f:
        pickle.dump(all_html_links, f, pickle.HIGHEST_PROTOCOL)

# Open all_html_links
def open_all_html_links():
    """ Open the pickle file 'all_html_links.pickle' """
    return pd.read_pickle('all_html_links.pickle')

# Open teams_and_dates.pickle
def open_teams_and_dates():
    """ Open the pickle file 'teams_and_dates.pickle' """
    return pd.read_pickle('teams_and_dates.pickle')

# Print QC information
def my_df_QC():
    """ Run random QC tests on my_df """
    print('Len my_df:', len(my_df))
    print('Max goals:', my_df['G'].max())
    print('Max goalscorer:', my_df[my_df['G'] == my_df['G'].max()].index[0])
    print('Max TOI:  ', my_df['TOI'].max())
    print('Max TOI Player:', my_df[my_df['TOI'] == my_df['TOI'].max()].index[0])
    print('Chris Chelios present:', 'Chris Chelios' in my_df.index)

#Open results from the 2000-2001 season, game-by-game df
def open_2000_2001_game_results():
    """ Open the pickle file '2000-2001-game-results.pickle' """
    return pd.read_pickle('2000-2001-game-results.pickle')

#Create new, blank variables
def restartAll():
    """A function to create a brand new statistical workspace"""
    user_input = input('Are you sure you want to clear all previous data? (y/n)    ')
    if user_input.lower() == 'y':

        #Create new, empty variables (dfs, etc)
        my_df = new_my_df()
        last_time_df = create_new_last_time_df()
        my_games_clean = {}
        all_time_clean_games = {}

        #Save all new variables
        save_my_df(my_df)
        save_last_time_df(last_time_df)
        save_my_games_clean(my_games_clean)
        save_all_time_clean_games(all_time_clean_games)

    else:
        pass

#Reset variables for each year's scrape
def yearlyRestart():
    """A function to create a mostly-new statistical workspace"""

    #Create new my_df
    my_df = new_my_df()

    #Save all new variables
    save_my_df(my_df)

'--------------- Call To Provided Functions ---------------'

if __name__ == '__main__':
    scrapeYear(2007)

'----------------------------------------------------------'

# my_df = open_yearly_my_df(years='2002_2003')
# my_df = open_my_df()
# all_html_links = open_all_html_links()
my_games_unclean = open_my_games_unclean()
my_games_clean = open_my_games_clean()
# teams_and_dates = open_teams_and_dates()
last_time_df = open_last_time_df()
# all_time_clean_games = open_all_time_clean_games()







