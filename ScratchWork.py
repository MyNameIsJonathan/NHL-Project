import pandas as pd
import numpy as np

my_data = pd.read_pickle('NHL_2008_to_2018')
my_data = my_data.fillna(0).replace({'-':0})

columns_to_int = ['Goal', 'Assists', 'GP', 'TOI', 'Shots', 'Rush', 'Rebounds', 
                  'PIM', 'Penalties', 'Minor', 'Major', 'Misconduct', 'Drawn', 
                  'Giveaways', 'Takeaways', 'Hits']

my_columns_to_int = [[a for a in my_data.columns if b in a] for b in columns_to_int]
my_columns_to_int = [item for sublist in my_columns_to_int for item in sublist]

my_data[my_columns_to_int] = my_data[my_columns_to_int].astype(int)

#Convert string %s to floats