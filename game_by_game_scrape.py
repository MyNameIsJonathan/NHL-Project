# Scrape the website https://www.hockey-reference.com for game-by-game stats

import pandas as pd
from My_Classes import person
from My_Classes import hockey_player
import pickle
import requests
from bs4 import BeautifulSoup
import datetime
import time


def gameStatsTotal(filename, home_team_name, away_team_name):

    # Read table from hockey-reference
    df = pd.read_html(filename, header=1)
    df_away = df[2].iloc[:-1, 1:18]
    df_home = df[4].iloc[:-1, 1:18]

    # Make 'Team' column
    df_away['Team'] = away_team_name
    df_home['Team'] = home_team_name

    #Combine the two teams' dataframes
    df = pd.concat([df_away, df_home])

    # Set player name to index
    df = df.set_index(['Team', 'Player'])

    # Delete columns that are only present in the datasets starting in 2014-2015 season
    cols_to_drop = ['EV.2', 'PP.2', 'SH.2', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17']
    df = df.drop([column for column in cols_to_drop if column in df.columns], axis=1)

    # Rename columns for better readability
    df = df.rename(columns = {'EV.1':'EV', 'PP.1':'PP', 'SH.1':'SH', 'SHFT':'Shifts'})

    #Fill NaN values to convert to int
    df = df.fillna(0)

    #Get int of minutes on ice
    df['TOI'] = df['TOI'].str.split(':')
    df['TOI'] = df['TOI'].apply(lambda x: int(x[0]) + int(x[1])/60)
    df['TOI'] = df['TOI'].round(2)
    
    return df

def getHTMLLinks(month, day, year):

    # Create the hockey-reference link for the day's games
    url = 'https://www.hockey-reference.com/boxscores/index.fcgi?month={}&day={}&year={}'.format(month, day, year)

    # Record team names for each game
    my_days_games = pd.read_html(url)
    my_home_teams = []
    my_away_teams = []

    # Iterate through returned list of dfs, to record home and away team names
    for i in range(0, len(my_days_games)-1, 2):
        my_home_teams.append(my_days_games[i].iloc[1, 0])
        my_away_teams.append(my_days_games[i].iloc[0, 0])

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

    # Return 1 - boxscore links, 2 - home team names, 3 - away team names
    return (boxscore_links, my_home_teams, my_away_teams)

def getStats(starting_df=None, start_date='2000/10/4', end_date='2000/12/01'):

    start_date = pd.to_datetime(start_date, format='%Y/%m/%d')
    end_date = pd.to_datetime(end_date, format='%Y/%m/%d')

    today = datetime.datetime.now().date()

    my_games = {}
    all_html_links = {}
    my_game_index = 0

    while start_date != end_date:
        # Get the html links for the tables
        my_html_results = getHTMLLinks(start_date.month, start_date.day, start_date.year)
        my_html_links = my_html_results[0]
        my_home_teams = my_html_results[1]
        my_away_teams = my_html_results[2]
        all_html_links[str(start_date)] = my_html_links
        start_date += datetime.timedelta(days=1)
    
    # Use these html links to create games' dataframes
    for i in range(len(my_html_links)):
        my_games[my_game_index] = gameStatsTotal(my_html_links[i], home_team_name=my_home_teams[i],  away_team_name=my_away_teams[i])
        my_game_index += 1
        time.sleep(1/5)

    with open('my_games.pickle', 'wb') as f:
        # Pickle the 'my_games' dictionary using the highest protocol available.
        pickle.dump(my_games, f, pickle.HIGHEST_PROTOCOL)

    # Create master df, initialized with first df in my_games dictionary &
    # Iterate through games' dfs, merging them into the main df, then adding their values to the main df (Ex: Adding Goal totals)
    if starting_df is None:
        my_df = my_games[0].copy(deep=True)
        for game in range(1, len(my_games)):
            my_df = my_df.add(my_games[game], fill_value=0)
    else:
        my_df = starting_df.copy(deep=True)
        for game in range(len(my_games)):
            my_df = my_df.add(my_games[game], fill_value=0)

    # Convert columns to int
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        if column in my_df.columns:
            my_df[column] = my_df[column].astype(int)

    return my_df


my_df = getStats(start_date='2000/10/4', end_date='2000/10/6')
# 32 games between 10/4 and 10/10, inclusive 

# Save my_df
with open('my_df.pickle', 'wb') as f:
    # Pickle the 'my_games' dictionary using the highest protocol available.
    pickle.dump(my_df, f, pickle.HIGHEST_PROTOCOL)

# open my_df
my_df = pd.read_pickle('my_df.pickle')

# Open my_games
my_games = pd.read_pickle('my_games.pickle')



