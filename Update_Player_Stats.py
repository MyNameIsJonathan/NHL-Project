"""

This file will hold the function UpdatePlayers(), that will scrape the web, add information to current NHL Dataset, and update players accordingly

"""

def UpdatePlayers():
    """The intent here is for this function to scrape NHL.com for recent stat updates during games, adding them to the player's current totals
    """
    return

from My_Classes import hockey_player, NHL_Team
import pandas as pd

my_data = pd.read_pickle('pickleFiles/RandomPickles/NHL_2008_to_2018')
my_data.index = [player.replace(u'\xa0', u' ') for player in my_data.index]

my_players_list = []

for player in list(my_data.index):
    this_player = hockey_player(name=player)
    this_player.team = my_data.loc[player, 'Team 2017_2018']
    this_player.position = my_data.loc[player, 'Position 2017_2018']
    my_players_list.append(this_player)