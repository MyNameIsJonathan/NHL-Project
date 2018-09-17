"""

This file is where I will import the data via a web-scrape and create the main dataframe from which analysis will draw

"""

import pandas as pd
from unicodedata import normalize

#Gather filenames for the complete season stats for all NHL players from 2008 through 2018
# filename_2017_2018 = 'https://www.naturalstattrick.com/playerteams.php?season=20172018&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
# filename_2016_2017 = 'https://www.naturalstattrick.com/playerteams.php?season=20162017&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
# filename_2015_2016 = 'https://www.naturalstattrick.com/playerteams.php?season=20152016&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
# filename_2014_2015 = 'https://www.naturalstattrick.com/playerteams.php?season=20142015&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
# filename_2013_2014 = 'https://www.naturalstattrick.com/playerteams.php?season=20132014&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
# filename_2012_2013 = 'https://www.naturalstattrick.com/playerteams.php?season=20122013&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
# filename_2011_2012 = 'https://www.naturalstattrick.com/playerteams.php?season=20112012&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
# filename_2010_2011 = 'https://www.naturalstattrick.com/playerteams.php?season=20102011&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
# filename_2009_2010 = 'https://www.naturalstattrick.com/playerteams.php?season=20092010&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
# filename_2008_2009 = 'https://www.naturalstattrick.com/playerteams.php?season=20082009&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'

#Read html tables into Pandas DataFrames, selecting the first table detected ([0]), saving these as pickles for reuse
# df_raw_2017_2018 = pd.read_html(filename_2017_2018)[0].to_pickle('df_raw_2017_2018')
# df_raw_2016_2017 = pd.read_html(filename_2016_2017)[0].to_pickle('df_raw_2016_2017')
# df_raw_2015_2016 = pd.read_html(filename_2015_2016)[0].to_pickle('df_raw_2015_2016')
# df_raw_2014_2015 = pd.read_html(filename_2014_2015)[0].to_pickle('df_raw_2014_2015')
# df_raw_2013_2014 = pd.read_html(filename_2013_2014)[0].to_pickle('df_raw_2013_2014')
# df_raw_2012_2013 = pd.read_html(filename_2012_2013)[0].to_pickle('df_raw_2012_2013')
# df_raw_2011_2012 = pd.read_html(filename_2011_2012)[0].to_pickle('df_raw_2011_2012')
# df_raw_2010_2011 = pd.read_html(filename_2010_2011)[0].to_pickle('df_raw_2010_2011')
# df_raw_2009_2010 = pd.read_html(filename_2009_2010)[0].to_pickle('df_raw_2009_2010')
# df_raw_2008_2009 = pd.read_html(filename_2008_2009)[0].to_pickle('df_raw_2008_2009')

# Read pickles to get dataframes
df_raw_2017_2018 = pd.read_pickle('df_raw_2017_2018')
df_raw_2016_2017 = pd.read_pickle('df_raw_2016_2017')
df_raw_2015_2016 = pd.read_pickle('df_raw_2015_2016')
df_raw_2014_2015 = pd.read_pickle('df_raw_2014_2015')
df_raw_2013_2014 = pd.read_pickle('df_raw_2013_2014')
df_raw_2012_2013 = pd.read_pickle('df_raw_2012_2013')
df_raw_2011_2012 = pd.read_pickle('df_raw_2011_2012')
df_raw_2010_2011 = pd.read_pickle('df_raw_2010_2011')
df_raw_2009_2010 = pd.read_pickle('df_raw_2009_2010')
df_raw_2008_2009 = pd.read_pickle('df_raw_2008_2009')

my_dfs = [
    df_raw_2017_2018,
    df_raw_2016_2017,
    df_raw_2015_2016,
    df_raw_2014_2015,
    df_raw_2013_2014,
    df_raw_2012_2013,
    df_raw_2011_2012,
    df_raw_2010_2011,
    df_raw_2009_2010,
    df_raw_2008_2009]

my_years = [
    '2017_2018',
    '2016_2017',
    '2015_2016',
    '2014_2015',
    '2013_2014',
    '2012_2013',
    '2011_2012',
    '2010_2011',
    '2009_2010',
    '2008_2009'
]

#The 2012-2013 year was truncated -- extrapolate data to mimic 82-game season
    # The following categories were multiplied by 1/0.5854, to bring them to an 82-game similar
    #GP, Goals, Total Assists, First Assists, Second Assists, Total Points, Shots, Rush Attempts, Rebounds Created, PIM, Giveaways, Takeaways, Hits, Hits Taken, Shots Blocked, Faceoffs Won, Faceoffs Lost
edited_columns = ['GP', 'Goals', 'Total Assists', 'First Assists', 'Second Assists', 
                  'Total Points', 'Shots', 'Rush Attempts', 'Rebounds Created', 'PIM', 
                  'Giveaways', 'Takeaways', 'Hits', 'Hits Taken', 'Shots Blocked', 
                  'Faceoffs Won', 'Faceoffs Lost']

#Perform mutiplication for year 2012_2013
df_raw_2012_2013[edited_columns] = round(df_raw_2012_2013[edited_columns] * 1/0.5854, 0)
df_raw_2012_2013[edited_columns] = df_raw_2012_2013[edited_columns].astype(int) #Convert resulting floats to ints

#Set player name as the index in each df
for df in my_dfs:
    df.set_index(['Player'], inplace=True)

#Rename columns to reflect years
for df in range(len(my_dfs)):
    my_dfs[df].columns = [str(col) + ' '  + my_years[df] for col in my_dfs[df].columns]

#Merge datasets
all_2008_2018 = (pd.merge(df_raw_2008_2009, df_raw_2009_2010, how='outer', left_index=True, right_index=True)
 .merge(df_raw_2010_2011, how='outer', left_index=True, right_index=True)
 .merge(df_raw_2011_2012, how='outer', left_index=True, right_index=True)
 .merge(df_raw_2012_2013, how='outer', left_index=True, right_index=True)
 .merge(df_raw_2013_2014, how='outer', left_index=True, right_index=True)
 .merge(df_raw_2014_2015, how='outer', left_index=True, right_index=True)
 .merge(df_raw_2015_2016, how='outer', left_index=True, right_index=True)
 .merge(df_raw_2016_2017, how='outer', left_index=True, right_index=True)
 .merge(df_raw_2017_2018, how='outer', left_index=True, right_index=True))

#Normalize the string text from the players' names in the index
all_2008_2018.index = [normalize("NFKD", player_name) for player_name in all_2008_2018.index]

#Drop the first, empty column from each DataFrame
all_2008_2018 = all_2008_2018.loc[:, ~all_2008_2018.columns.str.startswith('Unnamed:')]

# Create a Career Goals Column
all_2008_2018['Career Goals'] = all_2008_2018[['Goals ' + year for year in my_years]].sum(axis=1)

# Create a Career Assists Column too
all_2008_2018['Career Assists'] = all_2008_2018[['Total Assists ' + year for year in my_years]].sum(axis=1)

# Sort the dataframe by goals
all_2008_2018 = all_2008_2018.sort_values('Career Goals', ascending=False)

#Change all instances of '-' to 0
all_2008_2018 = all_2008_2018.replace({'-': 0})

#Fillna to replace NaN with 0
all_2008_2018 = all_2008_2018.fillna(0)

#Convert columns to int
columns_to_int = ['Goal', 'Assists', 'GP', 'TOI', 'Shots', 'Rush', 'Rebounds', 
                  'PIM', 'Penalties', 'Minor', 'Major', 'Misconduct', 'Drawn', 
                  'Giveaways', 'Takeaways', 'Hits']
#Select all columns that contain the keywords above, in columns_to_int
my_columns_to_int = [[a for a in all_2008_2018.columns if b in a] for b in columns_to_int]
#Convert my_columns_to_int from list of lists to single list
my_columns_to_int = [item for sublist in my_columns_to_int for item in sublist]

#Change selected columns
all_2008_2018[my_columns_to_int] = all_2008_2018[my_columns_to_int].astype(int)

#Select all columns that contain the word 'Faceoff', to convert from dtype Object to Float. Same process as above, for floats instead of ints
columns_to_float = ['Faceoffs']
my_columns_to_float = [[a for a in all_2008_2018.columns if b in a] for b in columns_to_float]
my_columns_to_float = [item for sublist in my_columns_to_float for item in sublist]
all_2008_2018[my_columns_to_float] = all_2008_2018[my_columns_to_float].astype(float)

# Save the dataframe. Length should = 2111
all_2008_2018.to_pickle('NHL_2008_to_2018')

