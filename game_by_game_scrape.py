# Scrape the website https://www.hockey-reference.com for game-by-game stats

import pandas as pd
from My_Classes import person
from My_Classes import hockey_player
import pickle
import requests
from bs4 import BeautifulSoup
import datetime
import time

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

def cleanUncleanGames():

    my_games_unclean = pd.read_pickle('my_games_unclean.pickle')
    my_games_clean = {}

    print('Number of games to clean = {}'.format(len(my_games_unclean)))

    for index, game in my_games_unclean.items():
        if 'SV%' not in game.columns:
            my_games_clean[index] = cleanGame(game)

    with open('my_games_clean.pickle', 'wb') as f:
        pickle.dump(my_games_clean, f, pickle.HIGHEST_PROTOCOL)

    print('Number of games cleaned = {}'.format(len(my_games_clean)))

def incorporateNewStats(my_df):

    """[updates my_df]
    
    Returns:
        [none] -- [just updates my_df]
    """

    my_games_clean = pd.read_pickle('my_games_clean.pickle')

    # Create master df, initialized with first df in my_games dictionary &
    # Iterate through games' dfs, merging them into the main df, then adding their values to the main df (Ex: Adding Goal totals)
    columns_to_add = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Shifts', 'TOI']

    for index, game in my_games_clean.items():
        my_df = my_df[columns_to_add].add(game[columns_to_add], fill_value=0) #This leaves NaN in the 'Date' column
        # Update the 'Date' column of the main df with the game's date, for each player who scored
        my_df.loc[game[game['G'] > 0].index, 'Date'] = game.loc[game['G'] > 0, 'Date']

    #Convert NaN in the 'Date' column to October 4, 2000
    my_df['Date'] = my_df['Date'].fillna('2000/10/4')

    # Convert columns to int
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        if column in my_df.columns:
            my_df[column] = my_df[column].astype(int)

    # Create a column 'Days Since Last Goal'
    today = pd.to_datetime('today')
    my_df['DateTime'] = pd.to_datetime(my_df['Date'], format='%Y/%m/%d')
    my_df['Days Since Last Goal'] = today - my_df['DateTime']
    my_df['Days Since Last Goal'] = my_df['Days Since Last Goal'].dt.days
    
    with open('my_stats_df.pickle', 'wb') as f:
        pickle.dump(my_df, f, pickle.HIGHEST_PROTOCOL)



def updateDF(df, startDate='2000/10/4', endDate='2000/10/10'):
    scrapeHTMLRange(startDate, endDate)
    scrapeAvailableGames()
    cleanUncleanGames()
    incorporateNewStats(df)



my_df = pd.read_pickle('my_stats_df.pickle')

updateDF(my_df, startDate='2000/10/10', endDate='2000/10/15')

"""

GLOBAL VARIABLE SECTION

"""


# Save my_df
# my_df = pd.DataFrame(columns=['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Shifts', 'TOI', 'Team', 'Date'])
# with open('my_df.pickle', 'wb') as f:
#     pickle.dump(my_df, f, pickle.HIGHEST_PROTOCOL)

# open my_df
my_df = pd.read_pickle('my_stats_df.pickle')

# Open my_games_unclean
my_games_unclean = pd.read_pickle('my_games_unclean.pickle')

# Open my_games_clean
my_games_clean = pd.read_pickle('my_games_clean.pickle')

# Open all_html_links
all_html_links = pd.read_pickle('all_html_links.pickle')

# Open teams_and_dates.pickle
teams_and_dates = pd.read_pickle('teams_and_dates.pickle')

# Potential next steps:
    # 1 - Further modularize the functions. I don't need to be questioning the database everytime, now that I have the date under control. 
    # 2 - Look into how the 'Days Since Last Goal' method can be applied to all the other categories!!

# Print QC information
# print('')
# print('Len my_df:', len(my_df))
# print('Max goals:', my_df['G'].max())
# print('Max TOI:  ', my_df['TOI'].max())
# print('Max TOI Player:', my_df[my_df['TOI'] == my_df['TOI'].max()].index[0])
# print('Chris Chelios present:', 'Chris Chelios' in my_df.index)


