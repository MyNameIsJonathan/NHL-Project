import pandas as pd
from My_Classes import person
from My_Classes import hockey_player
import pickle
import requests
from bs4 import BeautifulSoup
import datetime
import time


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
    # Rename columns for better readability
    df_away = df_away.rename(columns = {'EV.1':'EV', 'PP.1':'PP', 'SH.1':'SH', 'SHFT':'Shifts'})
    df_home = df_home.rename(columns = {'EV.1':'EV', 'PP.1':'PP', 'SH.1':'SH', 'SHFT':'Shifts'})
    #Fill NaN values to convert to int. Convert to in
    df_away = df_away.fillna(0)
    df_home = df_home.fillna(0)
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        df_away[column] = df_away[column].astype(int)
        df_home[column] = df_home[column].astype(int)
    #Convert time on ice from str to datetime, so that time on ice can be summed later
    df_away['TOI'] = pd.to_datetime(df_away['TOI'], format='%M:%S')
    df_home['TOI'] = pd.to_datetime(df_home['TOI'], format='%M:%S')
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


my_date = datetime.datetime(2000, 10, 4)
end_date = datetime.datetime(2000, 10, 7)
today = datetime.datetime.now().date()

my_games = {}


while my_date != end_date:
    # Get the html links for the tables
    my_html_links = get_html_links(my_date.month, my_date.day, my_date.year)
    # Use these html links to create games' dataframes
    for index, filename in enumerate(my_html_links):
        my_games[index] = game_stats_total(filename)
        time.sleep(1)
    my_date += datetime.timedelta(days=1)

if len(my_games) > 0:
    for game in range(1, len(my_games)):
        my_games[0].add(my_games[game], fill_value=0)

