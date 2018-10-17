

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