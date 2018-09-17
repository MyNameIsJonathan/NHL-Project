import pandas as pd
import numpy as np

my_data = pd.read_pickle('NHL_2008_to_2018')
my_data = my_data.fillna(0).replace({'-':0})




#Convert string %s to floats