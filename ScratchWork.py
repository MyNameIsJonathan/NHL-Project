import pandas as pd
from My_Classes import person
from My_Classes import hockey_player

#Initialize list of players
my_players_list = []

def game_stats(filename, my_players_list):

    """Scrapes the web for updated game-by-game stats, importing and cleaning data, appending it to the overaching dataframe
    
    Returns:
        None (can be edited to return the game's stats)
        [dataframe] -- [stats from the day's game]
    """

    # df = pd.read_html('https://www.hockey-reference.com/boxscores/201806070VEG.html')[0]
    # df.to_pickle('df_todays_game_trial')
    df = pd.read_pickle(filename).iloc[:, :5]
    df[2] = df[2].astype(str)
    df[2] = df[2].str.split()

    #Rename columns
    df.columns = ['Time', 'Team', 'Goal Scorer', 'Primary Assist', 'Secondary Assist']

    for i in range(len(df)):
        if len(df.iloc[i, 2]) < 8:
            my_length = len(df.iloc[i, 2])
            df.iloc[i, 2].extend(['-' for j in range(10 - my_length)])
        df.iloc[i, 3] = str(df.iloc[i, 2][-5]) + ' ' + str(df.iloc[i, 2][-4])
        df.iloc[i, 4] = str(df.iloc[i, 2][-2]) + ' ' + str(df.iloc[i, 2][-1])
        if str(df.iloc[i, 2][0]) == 'PP':
            df.iloc[i, 2] = str(df.iloc[i, 2][2]) + ' ' + str(df.iloc[i, 2][3])
        else:
            df.iloc[i, 2] = str(df.iloc[i, 2][0]) + ' ' + str(df.iloc[i, 2][1])

    #Only count rows of the df that are actual goals, not other information. Also, accomodate "PP" indication
    for player in range(len(df)):
        if df.iloc[player, 2][:3] == 'nan':
            pass
        elif df.iloc[player, 2][0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            pass
        else:
            current_player = hockey_player(name=df.iloc[player, 2], team=df.iloc[player, 1])
            my_players_list.append(current_player)

    #Remove period name from 'Time' column, create new 'Period' column
    df['Period'] = df.Time[df['Time'].str.contains('Period')]
    df['Period'] = df['Period'].fillna(method='ffill')

    #Convert 'Time' column to datetime
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
    df['Time'] = pd.DatetimeIndex(df['Time']).hour + pd.DatetimeIndex(df['Time']).minute

    #Remove rows that only served to indicate the period
    df = df[df['Time'].notnull()]

    #Set Period, Time Multiindex
    df = df.set_index(['Period', 'Time'])

    return df

a = game_stats('df_todays_game_trial', my_players_list)
