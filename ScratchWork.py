

end_year = 2006
my_file = 'https://www.hockey-reference.com/leagues/NHL_{}_games.html'.format(end_year)
my_years_df = pd.read_html(my_file)[0]
start_date = my_years_df.iloc[0, 0]
end_date = str(pd.to_datetime(my_years_df.iloc[-1, 0]).date() + datetime.timedelta(days=1))

my_links = pd.read_pickle('all_html_links_2005_2006.pickle')

for index, game in my_games_unclean.items():
    if 'SV%' in game.columns:
        print(index)

my_count = 0
for day, games in my_links.items():
    my_count += len(games)

print(my_count)

my_links[list(my_links.keys())[0]]

urls = ['https://www.hockey-reference.com/boxscores/200510050BOS.html',
 'https://www.hockey-reference.com/boxscores/200510050BUF.html',
 'https://www.hockey-reference.com/boxscores/200510050CHI.html']


my_url = urls[2]

df = pd.read_html(my_url, header=1)
df_away = df[2].iloc[:-1, 1:18].copy()
df_home = df[4].iloc[:-1, 1:18].copy()

# Make 'Team' column
df_away['Team'] = away_team_name
df_home['Team'] = home_team_name

#Combine the two teams' dataframes
df = pd.concat([df_away, df_home])

#Make a 'Date' column, which will eventually be used to represent the last time each player scored a goal
df['Date'] = game_date
df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d')
df['Date'] = df['Date'].dt.date

# Set player name to index
df = df.set_index('Player')

game_scrape = scrapeGame(urls[2], game_date=2005/10/5, home_team_name='Chicago Blackhawks', away_team_name='Mighty Ducks of Anaheim')


# open my_df
def open_my_df():
    """ Open the pickle file 'my_stats_df.pickle' """
    return pd.read_pickle('my_df.pickle')

#Open my_df from a specific year
def open_yearly_my_df(years='1999_2000'):
    """ Open the pickle file for a year's stats """
    my_filename = "my_df_{}.pickle".format(years)
    return pd.read_pickle(my_filename)

#Open yearly seasonSummary, containing url, date, home, and away teams
def open_yearly_seasonSummary(end_year=2000):
    """ Open the pickle file for a year's stats """
    my_filename = "seasonSummary_{}_{}.pickle".format(end_year-1, end_year)
    return pd.read_pickle(my_filename)

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

# Open all_time_clean_games dictionary
def open_all_time_clean_games():
    """ Open the pickle file 'all_time_clean_games.pickle' """
    return pd.read_pickle('all_time_clean_games.pickle')

# Open all_html_links
def open_all_html_links():
    """ Open the pickle file 'all_html_links.pickle' """
    return pd.read_pickle('all_html_links.pickle')

# Open teams_and_dates.pickle
def open_teams_and_dates():
    """ Open the pickle file 'teams_and_dates.pickle' """
    return pd.read_pickle('teams_and_dates.pickle')

#Open results from the 2000-2001 season, game-by-game df
def open_2000_2001_game_results():
    """ Open the pickle file '2000-2001-game-results.pickle' """
    return pd.read_pickle('2000-2001-game-results.pickle')


# Create master df, initialized with first df in my_games dictionary &
# Iterate through games' dfs, merging them into the main df, then adding their values to the main df (Ex: Adding Goal totals)
columns_to_add = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Shifts', 'TOI']

#Keep only these columns -- removes 'Date' column, which is in last_time_df
my_df = my_df[columns_to_add]


#Add this day's games df to my_df
my_df = my_df.add(new_df[columns_to_add], fill_value=0) 

# Use unclean games to get min and max dates 
my_games_unclean = pd.read_pickle('my_games_unclean_{}_{}.pickle'.format(start_year, end_year))
unclean_df = pd.concat([game for game in my_games_unclean.values()])
my_key = 'Dates: {} to {}'.format(unclean_df['Date'].min(), unclean_df['Date'].max())

# Move games from my_games_clean dict to all_time_clean_games
all_time_clean_games = open_all_time_clean_games()
all_time_clean_games[my_key] = list(my_games_clean.values())
if len(all_time_clean_games[my_key]) == len(my_games_clean):
my_games_clean = {}
savePickle(my_games_clean, 'my_games_clean', start_year, end_year)
savePickle(all_time_clean_games, 'all_time_clean_games', start_year, end_year)
else:
raise LengthException('Number of clean games does not equal length of preserved games val')

print('My_games_clean now empty:', len(my_games_clean) == 0)
print('Games added to all_time_clean_games:', len(all_time_clean_games[my_key]))

# Create a new, empty my_df
def new_my_df():
    """ Create a new, empty my_df """
    return pd.DataFrame(columns=['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S', 'Shifts', 'TOI', 'Team', 'Date'])

