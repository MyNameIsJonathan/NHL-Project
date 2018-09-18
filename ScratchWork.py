import pandas as pd
from My_Classes import person
from My_Classes import hockey_player

def game_stats(filename):

    # df = pd.read_html('https://www.hockey-reference.com/boxscores/201806070VEG.html')[0]
    # df.to_pickle('df_todays_game_trial')
    df = pd.read_pickle(filename).iloc[:, :5]
    df[2] = df[2].astype(str)
    df[2] = df[2].str.split()

    #Remove period name from 'Time' column, create new 'Period' column
    # df['Period'] = df[df['Time'].contains('Period')]

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

    #Initialize list of platers
    my_players = []

    #Only count rows of the df that are actual goals, not other information. Also, accomodate "PP" indication
    for player in range(len(df)):
        if df.iloc[player, 2][:3] == 'nan':
            pass
        elif df.iloc[player, 2][0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            pass
        else:
            current_player = hockey_player(name=df.iloc[player, 2], team=df.iloc[player, 1])
            my_players.append(current_player)

    for player in my_players:
        print(player)
    
    return my_players

game_stats('df_todays_game_trial')
