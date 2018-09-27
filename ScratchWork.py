import pandas as pd
from game_by_game_scrape import getHTMLLinks
import datetime

start_date = '2000/10/4'
end_date = '2000/10/10'

start_date = pd.to_datetime(start_date, format='%Y/%m/%d')
end_date = pd.to_datetime(end_date, format='%Y/%m/%d')

