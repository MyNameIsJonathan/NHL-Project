# Scrape the website https://www.hockey-reference.com for game-by-game stats

import pandas as pd

link = 'https://www.nhl.com/gamecenter/phi-vs-nyi/2018/09/16/2018010003/recap/box-score#game=2018010003,game_state=final,lock_state=final,game_tab=box-score'

my_df = pd.read_html(link)[0]

a = my_df.iloc[3, 2].split()