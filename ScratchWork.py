import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

my_data = pd.read_pickle('NHL_2008_to_2018')
my_data = my_data.fillna(0).replace({'-':0})

sns.set(style="ticks")
x = my_data[my_data['Faceoffs % 2016_2017'] > 1]['Faceoffs % 2016_2017'].values[:len(my_data[my_data['Faceoffs % 2016_2017'] > 1])]
y = my_data[my_data['Faceoffs % 2017_2018'] > 1]['Faceoffs % 2017_2018'].values[:len(my_data[my_data['Faceoffs % 2016_2017'] > 1])]
sns.jointplot(x, y, kind="hex", color="#4CB391")
plt.show()

#Convert string %s to floats