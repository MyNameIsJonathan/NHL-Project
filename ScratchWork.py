import pandas as pd
from My_Classes import person
from My_Classes import hockey_player
import pickle
import requests
from bs4 import BeautifulSoup
import datetime
import time

#FIX MINUTES AND SECONDS TOI

def game_stats_total(filename):
    # Read table from hockey-reference
    df = pd.read_html(filename, header=1)
    # except ValueError:
    #     return
    df_away = df[2].iloc[:-1, 1:18]
    df_home = df[4].iloc[:-1, 1:18]
    # Set player name to index
    df_away = df_away.set_index('Player')
    df_home = df_home.set_index('Player')
    # Delete columns that are only present in the datasets starting in 2014-2015 season
    cols_to_drop = ['EV.2', 'PP.2', 'SH.2', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17']
    df_away = df_away.drop([column for column in cols_to_drop if column in df_away.columns], axis=1)
    df_home = df_home.drop([column for column in cols_to_drop if column in df_home.columns], axis=1)
    # Rename columns for better readability
    df_away = df_away.rename(columns = {'EV.1':'EV', 'PP.1':'PP', 'SH.1':'SH', 'SHFT':'Shifts'})
    df_home = df_home.rename(columns = {'EV.1':'EV', 'PP.1':'PP', 'SH.1':'SH', 'SHFT':'Shifts'})
    #Fill NaN values to convert to int. Convert to in
    df_away = df_away.fillna(0)
    df_home = df_home.fillna(0)
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        if column in df_away.columns:
            df_away[column] = df_away[column].astype(int)
        if column in df_home.columns:
            df_home[column] = df_home[column].astype(int)
    #Get int of minutes on ice
    df_away['TOI'] = int(df_away['TOI'].str.split(':')[0][0]) + int(df_away['TOI'].str.split(':')[0][1])
    # df_away['TOI'] = int(df_away['TOI'][0][0]) + int(df_away['TOI'][0][1])/60
    df_home['TOI'] = int(df_home['TOI'].str.split(':')[0][0]) + int(df_home['TOI'].str.split(':')[0][1])
    # df_home['TOI'] = int(df_home['TOI'][0][0]) + int(df_home['TOI'][0][1])/60
    #Convert time on ice from str to datetime, so that time on ice can be summed later
    # df_away['TOI'] = pd.to_datetime(df_away['TOI'], format='%M:%S')
    # df_home['TOI'] = pd.to_datetime(df_home['TOI'], format='%M:%S')
    # #Convert to number of minutes (int) on ice to save significant memory and make adding easy
    # df_away['TOI'] = round(df_away['TOI'].dt.minute + df_away['TOI'].dt.second/60, 2)
    # df_home['TOI'] = round(df_home['TOI'].dt.minute + df_home['TOI'].dt.second/60, 2)
    # return (df_away, df_home)
    return pd.concat([df_away, df_home])

def get_html_links(month, day, year):
    url = 'https://www.hockey-reference.com/boxscores/index.fcgi?month={}&day={}&year={}'.format(month, day, year)
    r = requests.get(url)
    html_content = r.text
    soup = BeautifulSoup(html_content, 'lxml')
    links = soup.find_all('a')
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    boxscore_links = []
    for link in links:
        if link[:10] == '/boxscores':
            boxscore_links.append('www.hockey-reference.com' + link)
    boxscore_links = boxscore_links[5:-7]
    boxscore_links = ['https://' + link for link in boxscore_links]
    return boxscore_links

def create_stats_table(start_date='2000/10/4', end_date='2000/10/7'):

    start_date = pd.to_datetime(start_date, format='%Y/%m/%d')
    end_date = pd.to_datetime(end_date, format='%Y/%m/%d')

    today = datetime.datetime.now().date()

    my_games = {}
    all_html_links = {}
    my_game_index = 0

    while start_date != end_date:
        # Get the html links for the tables
        my_html_links = get_html_links(start_date.month, start_date.day, start_date.year)
        all_html_links[str(start_date)] = my_html_links
        # Use these html links to create games' dataframes
        for index, filename in enumerate(my_html_links):
            my_games[my_game_index] = game_stats_total(filename)
            my_game_index += 1
            time.sleep(1/2)
        start_date += datetime.timedelta(days=1)

    my_df = my_games[0].copy(deep=True)
    for game in range(1, len(my_games)):
        my_df = pd.concat([my_df, my_games[game]], join='outer')
        my_df = my_df.add(my_games[game], fill_value=0)

    return my_df

my_df = create_stats_table(start_date='2000/10/4', end_date='2000/10/5')

a = pd.DataFrame(['12:13', '13:14'], index=['Guy 1', 'Guy 2'])