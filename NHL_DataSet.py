"""

This file is where I will import the data via a web-scrape and create the main dataframe from which analysis will draw

"""


import pandas as pd
import matplotlib.pyplot as plt


#Gather filenames for the complete season stats for all NHL players from 2008 through 2018
filename_2017_2018 = 'https://www.naturalstattrick.com/playerteams.php?season=20172018&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
filename_2016_2017 = 'https://www.naturalstattrick.com/playerteams.php?season=20162017&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
filename_2015_2016 = 'https://www.naturalstattrick.com/playerteams.php?season=20152016&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
filename_2014_2015 = 'https://www.naturalstattrick.com/playerteams.php?season=20142015&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
filename_2013_2014 = 'https://www.naturalstattrick.com/playerteams.php?season=20132014&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
filename_2012_2013 = 'https://www.naturalstattrick.com/playerteams.php?season=20122013&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
filename_2011_2012 = 'https://www.naturalstattrick.com/playerteams.php?season=20112012&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
filename_2010_2011 = 'https://www.naturalstattrick.com/playerteams.php?season=20102011&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
filename_2009_2010 = 'https://www.naturalstattrick.com/playerteams.php?season=20092010&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'
filename_2008_2009 = 'https://www.naturalstattrick.com/playerteams.php?season=20082009&stype=2&sit=all&score=all&stdoi=std&rate=n&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=82&lines=single'

#Read html tables into Pandas DataFrames, selecting the first table detected ([0])
df_raw_2017_2018 = pd.read_html(filename_2017_2018)[0]
df_raw_2016_2017 = pd.read_html(filename_2016_2017)[0]
df_raw_2015_2016 = pd.read_html(filename_2015_2016)[0]
df_raw_2014_2015 = pd.read_html(filename_2014_2015)[0]
df_raw_2013_2014 = pd.read_html(filename_2013_2014)[0]
df_raw_2012_2013 = pd.read_html(filename_2012_2013)[0]
df_raw_2011_2012 = pd.read_html(filename_2011_2012)[0]
df_raw_2010_2011 = pd.read_html(filename_2010_2011)[0]
df_raw_2009_2010 = pd.read_html(filename_2009_2010)[0]
df_raw_2008_2009 = pd.read_html(filename_2008_2009)[0]


#Drop the first, empty column from each DataFrame
df_raw_2017_2018 = df_raw_2017_2018.drop(['Unnamed: 0'], axis=1)
df_raw_2016_2017 = df_raw_2016_2017.drop(['Unnamed: 0'], axis=1)
df_raw_2015_2016 = df_raw_2015_2016.drop(['Unnamed: 0'], axis=1)
df_raw_2014_2015 = df_raw_2014_2015.drop(['Unnamed: 0'], axis=1)
df_raw_2013_2014 = df_raw_2013_2014.drop(['Unnamed: 0'], axis=1)
df_raw_2012_2013 = df_raw_2012_2013.drop(['Unnamed: 0'], axis=1)
df_raw_2011_2012 = df_raw_2011_2012.drop(['Unnamed: 0'], axis=1)
df_raw_2010_2011 = df_raw_2010_2011.drop(['Unnamed: 0'], axis=1)
df_raw_2009_2010 = df_raw_2009_2010.drop(['Unnamed: 0'], axis=1)
df_raw_2008_2009 = df_raw_2008_2009.drop(['Unnamed: 0'], axis=1)

#The 2012-2013 year was truncated -- extrapolate data to mimic 82-game season
    # The following categories were multiplied by 1/0.5854, to bring them to an 82-game similar
    #GP, Goals, Total Assists, First Assists, Second Assists, Total Points, Shots, Rush Attempts, Rebounds Created, PIM, Giveaways, Takeaways, Hits, Hits Taken, Shots Blocked, Faceoffs Won, Faceoffs Lost

edited_columns = ['GP', 'Goals', 'Total Assists', 'First Assists', 'Second Assists', 'Total Points', 'Shots', 'Rush Attempts', 'Rebounds Created', 'PIM', 'Giveaways', 'Takeaways', 'Hits', 'Hits Taken', 'Shots Blocked', 'Faceoffs Won', 'Faceoffs Lost']

#Create manipulable copies of each DataFrame
df_2017_2018 = df_raw_2017_2018.copy()
df_2016_2017 = df_raw_2016_2017.copy()
df_2015_2016 = df_raw_2015_2016.copy()
df_2014_2015 = df_raw_2014_2015.copy()
df_2013_2014 = df_raw_2013_2014.copy()
df_2012_2013 = df_raw_2012_2013.copy()
df_2011_2012 = df_raw_2011_2012.copy()
df_2010_2011 = df_raw_2010_2011.copy()
df_2009_2010 = df_raw_2009_2010.copy()
df_2008_2009 = df_raw_2008_2009.copy()

#Perform mutiplication for year 2012_2013
df_2012_2013[edited_columns] = round(df_2012_2013[edited_columns] * 1/0.5854, 0)
df_2012_2013[edited_columns] = df_2012_2013[edited_columns].astype(int) #Convert resulting floats to ints

# Select for these columns:
columns_to_keep = ['Player', 'GP', 'Goals', 'Total Assists', 'Total Points']

df_2017_2018 = df_2017_2018[columns_to_keep]
df_2016_2017 = df_2016_2017[columns_to_keep]
df_2015_2016 = df_2015_2016[columns_to_keep]
df_2014_2015 = df_2014_2015[columns_to_keep]
df_2013_2014 = df_2013_2014[columns_to_keep]
df_2012_2013 = df_2012_2013[columns_to_keep]
df_2011_2012 = df_2011_2012[columns_to_keep]
df_2010_2011 = df_2010_2011[columns_to_keep]
df_2009_2010 = df_2009_2010[columns_to_keep]
df_2008_2009 = df_2008_2009[columns_to_keep]


# Set player as the index for all DataFrames
df_2017_2018.set_index('Player', inplace=True)
df_2016_2017.set_index('Player', inplace=True)
df_2015_2016.set_index('Player', inplace=True)
df_2014_2015.set_index('Player', inplace=True)
df_2013_2014.set_index('Player', inplace=True)
df_2012_2013.set_index('Player', inplace=True)
df_2011_2012.set_index('Player', inplace=True)
df_2010_2011.set_index('Player', inplace=True)
df_2009_2010.set_index('Player', inplace=True)
df_2008_2009.set_index('Player', inplace=True)


#Rename columns to reflect years
df_2017_2018.columns = [str(col) + ' 2017_2018' for col in df_2017_2018.columns]
df_2016_2017.columns = [str(col) + ' 2016_2017' for col in df_2016_2017.columns]
df_2015_2016.columns = [str(col) + ' 2015_2016' for col in df_2015_2016.columns]
df_2014_2015.columns = [str(col) + ' 2014_2015' for col in df_2014_2015.columns]
df_2013_2014.columns = [str(col) + ' 2013_2014' for col in df_2013_2014.columns]
df_2012_2013.columns = [str(col) + ' 2012_2013' for col in df_2012_2013.columns]
df_2011_2012.columns = [str(col) + ' 2011_2012' for col in df_2011_2012.columns]
df_2010_2011.columns = [str(col) + ' 2010_2011' for col in df_2010_2011.columns]
df_2009_2010.columns = [str(col) + ' 2009_2010' for col in df_2009_2010.columns]
df_2008_2009.columns = [str(col) + ' 2008_2009' for col in df_2008_2009.columns]


#Create master DF across all years, per player
all_2008_2018 = (pd.merge(df_2008_2009, df_2009_2010, how='outer', left_index=True, right_index=True)
 .merge(df_2010_2011, how='right', left_index=True, right_index=True)
 .merge(df_2011_2012, how='right', left_index=True, right_index=True)
 .merge(df_2012_2013, how='right', left_index=True, right_index=True)
 .merge(df_2013_2014, how='right', left_index=True, right_index=True)
 .merge(df_2014_2015, how='right', left_index=True, right_index=True)
 .merge(df_2015_2016, how='right', left_index=True, right_index=True)
 .merge(df_2016_2017, how='right', left_index=True, right_index=True)
 .merge(df_2017_2018, how='right', left_index=True, right_index=True))

# Select top 6 goal scorers from 2008 to 2018
all_2008_2018['Career Goals'] = all_2008_2018[['Goals 2008_2009', 
                                                  'Goals 2009_2010',  
                                                  'Goals 2010_2011', 
                                                  'Goals 2011_2012', 
                                                  'Goals 2012_2013', 
                                                  'Goals 2013_2014', 
                                                  'Goals 2014_2015', 
                                                  'Goals 2015_2016', 
                                                  'Goals 2016_2017', 
                                                  'Goals 2017_2018']].sum(axis=1)
# Get total assists too

all_2008_2018['Career Assists'] = all_2008_2018[['Total Assists 2008_2009', 
                                                  'Total Assists 2009_2010',  
                                                  'Total Assists 2010_2011', 
                                                  'Total Assists 2011_2012', 
                                                  'Total Assists 2012_2013', 
                                                  'Total Assists 2013_2014', 
                                                  'Total Assists 2014_2015', 
                                                  'Total Assists 2015_2016', 
                                                  'Total Assists 2016_2017', 
                                                  'Total Assists 2017_2018']].sum(axis=1)


all_2008_2018 = all_2008_2018.sort_values('Career Goals', ascending=False)

all_2008_2018.to_pickle('NHL_2008_to_2018')