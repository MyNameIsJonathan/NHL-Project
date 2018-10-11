import game_by_game_scrape


new_index = last_time_df.index.union(df.index)

last_time_df = last_time_df.reindex(new_index, fill_value='2000/10/5')

new_index = my_games_clean[1].index.union(last_time_df.index)


cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']
game_date = df['Date'].mode()


for column in cols:
    last_time_df.loc[df[df[column] > 0].index, column] = game_date[0]

