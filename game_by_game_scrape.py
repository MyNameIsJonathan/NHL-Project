# Scrape the website https://www.hockey-reference.com for game-by-game stats

import pandas as pd
from My_Classes import person
from My_Classes import hockey_player
import pickle
import requests
from bs4 import BeautifulSoup
import datetime
import time

#Fix updateLastTime to actually edit last_time_df

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

def scrapeHTMLRange(start_date, end_date):

    """[scrapes all html links for each each between the given dates, exclusive of the end date, storing them in the file all_html_links.pickle'.
    """

    start_date = pd.to_datetime(start_date, format='%Y/%m/%d')
    end_date = pd.to_datetime(end_date, format='%Y/%m/%d')
    all_html_links = {}

    total_home_teams = []
    total_away_teams = []
    all_game_dates = []

    # Get the html links for the tables
    while start_date != end_date:
        my_html_results = getHTMLLinks(start_date.month, start_date.day, start_date.year)
        all_html_links[str(start_date)] = my_html_results[0]
        total_home_teams.extend(my_html_results[1])
        total_away_teams.extend(my_html_results[2])
        all_game_dates.extend(my_html_results[3])
        start_date += datetime.timedelta(days=1)
        time.sleep(1/5)

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

    return teams_and_dates

def scrapeGame(my_url, game_date, home_team_name, away_team_name):

    """[Function to pull stats from a single game, given the url (attained through getHTMLLinks), the date (also from getHTMLLinks), home and away teams]
    Returns:
        [Pandas DataFrame] -- [a clean df that has the game's stats]
    """

    # Read table from hockey-reference
    df = pd.read_html(my_url, header=1)
    df_away = df[2].iloc[:-1, 1:18]
    df_home = df[4].iloc[:-1, 1:18]

    # Make 'Team' column
    df_away['Team'] = away_team_name
    df_home['Team'] = home_team_name

    #Combine the two teams' dataframes
    df = pd.concat([df_away, df_home])

    #Make a 'Date' column, which will eventually be used to represent the last time each player scored a goal
    df['Date'] = game_date
    my_df['Date'] = pd.to_datetime(my_df['Date'], format='%Y/%m/%d')

    # Set player name to index
    df = df.set_index('Player')

    return df

def scrapeAvailableGames():

    """[scrapes game data in file 'teams_and_dates.pickle' incorporating the resulting dfs into the file 'my_games_unclean.pickle']
    """

    teams_and_dates = pd.read_pickle('teams_and_dates.pickle')

    print('Number of games to scrape = {}'.format(len(teams_and_dates.columns)))

    my_games_unclean = {}

    # Use  html links to create games' dataframes
    for game in range(len(teams_and_dates.columns)):
        my_games_unclean[game] = scrapeGame(
            my_url=teams_and_dates.iloc[3, game], 
            game_date=teams_and_dates.iloc[2, game],
            home_team_name=teams_and_dates.iloc[0, game],
            away_team_name=teams_and_dates.iloc[1, game])
        time.sleep(1/5)

    # Pickle the 'my_games' dictionary using the highest protocol available.
    with open('my_games_unclean.pickle', 'wb') as f:
        pickle.dump(my_games_unclean, f, pickle.HIGHEST_PROTOCOL)

    print('Number of games scraped = {}'.format(len(my_games_unclean)))

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

    #Convert Date to datetime, if it's not already
    my_df['Date'] = pd.to_datetime(my_df['Date'], format='%Y/%m/%d')

    #Get int of minutes on ice from string "mm:ss"
    df['TOI'] = df['TOI'].str.split(':')
    df['TOI'] = df['TOI'].apply(lambda x: int(x[0]) + int(x[1])/60)
    df['TOI'] = df['TOI'].round(2)
    
    return df

def cleanUncleanGames():

    """[Cleans the data present in each game of my_games_unclean dictionary]
    """

    my_games_unclean = pd.read_pickle('my_games_unclean.pickle')
    my_games_clean = {}

    print('Number of games to clean = {}'.format(len(my_games_unclean)))

    for index, game in my_games_unclean.items():
        if 'SV%' not in game.columns:
            my_games_clean[index] = cleanGame(game)

    with open('my_games_clean.pickle', 'wb') as f:
        pickle.dump(my_games_clean, f, pickle.HIGHEST_PROTOCOL)

    print('Number of games cleaned = {}'.format(len(my_games_clean)))

def updateLastTime():

    """Update df containing the dates of the last time each player scored, hit, etc"""

    #Load in last_time_df
    last_time_df = open_last_time_df()

    #Load my_games_clean dictionary
    my_games_clean = open_my_games_clean()

    #Set columns to iterate through
    cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    #Iterate through all games in my_games_clean dictionary
    for index, game_df in my_games_clean.items():

        #Create the new index, which is a union of the main one and the one from the specific game
        new_index = last_time_df.index.union(game_df.index)
        #Implement the new index, filling in empty values with the date '2000/10/4' (start of '00 season)
        last_time_df = last_time_df.reindex(new_index, fill_value=pd.to_datetime('2000/10/3', format='%Y/%m/%d'))
        #Collect the date of the game
        game_date = game_df['Date'].mode()

        #Iterate through columns to update date for goals, assists, etc.
        for column in cols:
            last_time_df.loc[game_df[game_df[column] > 0].index, column] = game_date[0]

        last_time_df.loc[game_df.index, 'Last Game Date'] = game_date[0]

    #Save last_time_df
    save_last_time_df()

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

    #Create main df for all day's games
    new_df = pd.concat([game for game in my_games_clean.values()])

    #Combine stats for each player, between games
    new_df = new_df.groupby(new_df.index).sum()

    #Save new_df
    with open('new_df.pickle', 'wb') as f:
        pickle.dump(new_df, f, pickle.HIGHEST_PROTOCOL)

    #Add this day's games df to my_df
    my_df[columns_to_add] = my_df[columns_to_add].add(new_df[columns_to_add], fill_value=0) #ADD LAST GOAL DATA COLUMN, ASSIST TOO

    #Convert NaN in the 'Date' column to October 4, 2000
    my_df['Date'] = my_df['Date'].fillna('2000/10/4')

    # Convert columns to int
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        if column in my_df.columns:
            my_df[column] = my_df[column].astype(int)

    # Convery 'Date' column to datetime
    my_df['Date'] = pd.to_datetime(my_df['Date'], format='%Y/%m/%d')

    with open('my_stats_df.pickle', 'wb') as f:
        pickle.dump(my_df, f, pickle.HIGHEST_PROTOCOL)

def updateDF(df, startDate='2000/10/4', endDate='2000/10/10'):
    """ Run all prescribed functions on my_df, pulling html links, game data, then incorporating it to the file 'my_df.pickle' """
    scrapeHTMLRange(startDate, endDate)
    scrapeAvailableGames()
    cleanUncleanGames()
    updateLastTime()
    incorporateNewStats(df)



# Create a new, empty my_df
def new_my_df():
    """ Create a new, empty my_df """
    return pd.DataFrame(columns=['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Shifts', 'TOI', 'Team', 'Date'])

#Save my_df as a pickle file
def save_my_df():
    """ Save my_df as a pickle file """
    with open('my_df.pickle', 'wb') as f:
        pickle.dump(my_df, f, pickle.HIGHEST_PROTOCOL)

# open my_df
def open_my_df():
    """ Open the pickle file 'my_stats_df.pickle' """
    return pd.read_pickle('my_stats_df.pickle')

def create_new_last_time_df():
    """ Create a new last_time_df file """
    return pd.DataFrame(columns=['G', 'A', 'PTS', '+', '-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Last Game Date'])

# Save last_time_df as pickle file
def save_last_time_df():
    """ Save last_time_df as a pickle file """
    with open('last_time_df.pickle', 'wb') as f:
        pickle.dump(last_time_df, f, pickle.HIGHEST_PROTOCOL)

# Open last_time_df pickle file
def open_last_time_df():
    """ Open the pickle file 'last_time_df.pickle' """
    return pd.read_pickle('last_time_df.pickle')

# Open my_games_unclean
def open_my_games_unclean():
    """ Open the pickle file 'my_games_unclean.pickle' """
    return pd.read_pickle('my_games_unclean.pickle')

# Open my_games_clean
def open_my_games_clean():
    """ Open the pickle file 'my_games_clean.pickle' """
    return pd.read_pickle('my_games_clean.pickle')

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




# if __name__ == '__main__':
#     my_df = open_my_df()
#     updateDF(my_df, startDate='2000/10/10', endDate='2000/10/15')


last_time_df = create_new_last_time_df()
updateLastTime()
last_time_df = open_last_time_df()
