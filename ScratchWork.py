def scrapeSpecificDaysURLS(date='2000-12-31'):

    """[scrapes all html links for the given date storing them in a piclkle file labeled by day'.
    """

    myDate = pd.to_datetime(date, format='%Y-%m-%d')

    daily_html_links = {}

    total_home_teams = []
    total_away_teams = []
    all_game_dates = []

    print('Scraping game links for games on {}'.format(myDate))

    # Get the html links for the tables
    my_html_results = getURLS(myDate.month, myDate.day, myDate.year)
    daily_html_links[str(myDate)] = my_html_results[0]
    total_home_teams.extend(my_html_results[1])
    total_away_teams.extend(my_html_results[2])
    all_game_dates.extend(my_html_results[3])

    # Pickle the 'daily_html_links' dict using the highest protocol available.
    savePickle(daily_html_links, 'dailyHTMLLinks/dailyHTMLLinks_{}'.format(myDate))

    # Flatten list of game htmls
    flat_list_game_links = [item for sublist in list(daily_html_links.values()) for item in sublist]

    #Save home teams, away teams, and game dates in df
    teams_and_dates = pd.DataFrame([total_home_teams, total_away_teams, all_game_dates, flat_list_game_links])
    teams_and_dates = teams_and_dates.transpose()
    savePickle(teams_and_dates, 'dailyTeamsAndDates/dailyTeamsAndDates_{}'.format(myDate))

    print('Total game links scraped = {}'.format(len(teams_and_dates)))

def scrapeSpecificDaysGames(date='2000-1-1'): 

    myDate = pd.to_datetime(date, format='%Y-%m-%d')

    #Create my_games_unclean dict to store scraped games
    dailyGamesUnclean = {}

    daysGames = pd.read_pickle('dailyTeamsAndDates/dailyTeamsAndDates_{}.pickle'.format(myDate))
    number_of_games = len(daysGames)
    print('Number of games to scrape = {}'.format(number_of_games))

    #Instantiate counter for reporting scrape progress and create % thresholds
    my_count = 0
    threshold_25 = int(number_of_games*0.25)
    threshold_50 = int(number_of_games*0.5)
    threshold_75 = int(number_of_games*0.75)

    # Use  html links to create games' dataframes
    for game in range(number_of_games):
        dailyGamesUnclean[game] = scrapeGame(
            my_url=daysGames.iloc[game, 3], 
            game_date=daysGames.iloc[game, 2],
            home_team_name=daysGames.iloc[game, 0],
            away_team_name=daysGames.iloc[game, 1])
        my_count += 1
        if my_count == threshold_25:
            print("Scraped 25% of total games")
        elif my_count == threshold_50:
            print("Scraped 50% of total games")
        elif my_count == threshold_75:
            print("Scraped 75% of total games")
    
    # Pickle the 'my_games' dictionary using the highest protocol available.
    savePickle(dailyGamesUnclean, 'dailyGamesUnclean/dailyGamesUnclean_{}'.format(myDate))

    print('Number of games scraped = {}'.format(len(dailyGamesUnclean)))

def cleanSpecificDaysGames(date='2000-1-1'):

    myDate = pd.to_datetime(date, format='%Y-%m-%d')

    my_games_unclean = pd.read_pickle('dailyGamesUnclean/dailyGamesUnclean_{}.pickle'.format(myDate))
    my_games_clean = {}

    print('Number of games to clean = {}'.format(len(my_games_unclean)))

    for index, game in my_games_unclean.items():
        my_games_clean[index] = cleanGame(game)

    savePickle(my_games_clean, 'dailyGamesClean/dailyGamesClean_{}'.format(myDate))

    print('Number of games cleaned  = {}'.format(len(my_games_clean)))

def updateSpecificDaysLastTime(date='2000-1-1'):

    print("Updating Last Time to reflect new stats' dates")

    myDate = pd.to_datetime(date, format='%Y-%m-%d')

    #Load in last_time_df from the previous day, which will be copied and updated
    last_time_df = pd.read_pickle('dailyLastTime/dailyLastTime_{}.pickle'.format(myDate - datetime.timedelta(days=1))).copy()

    #Load my_games_clean dictionary
    my_games_clean = pd.read_pickle('dailyGamesClean/dailyGamesClean_{}.pickle'.format(myDate))

    #Set columns to iterate through
    cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    #Also add in last times the player was + or -
    pmCols = ['+', '-']

    #Iterate through all games in my_games_clean dictionary
    for index, game_df in my_games_clean.items():

        #Create the new index, which is a union of the main one and the one from the specific game
        new_index = last_time_df.index.union(game_df.index)
        #Implement the new index, filling in empty values with the date '2000/10/4' (start of '00 season)
        last_time_df = last_time_df.reindex(new_index, fill_value=datetime.date(2000,10,3))
        #Collect the date of the game
        game_date = game_df['Date'].mode()

        #Iterate through columns to update date for goals, assists, etc.
        for column in cols:
            last_time_df.loc[game_df[game_df[column] > 0].index, column] = game_date[0]

        #Set last game date to current game's date
        last_time_df.loc[game_df.index, 'Last Game Date'] = game_date[0]

        #Iterate through columns to edit +/- columns
        for column in pmCols:
            if column == '+':
                last_time_df.loc[game_df[game_df['+/-'] > 0].index, column] = game_date[0]
            elif column == '-':
                last_time_df.loc[game_df[game_df['+/-'] < 0].index, column] = game_date[0]

    #Save only the date, not the time
    for column in last_time_df.columns:
        try:
            last_time_df[column] = last_time_df[column].dt.date
        except AttributeError:
            pass

    #Save last_time_df
    savePickle(last_time_df, 'dailyLastTime/dailyLastTime_{}'.format(myDate))

def updateSpecificDaysSince(date='2000-1-1'):

    myDate = pd.to_datetime(date, format='%Y-%m-%d')

    print("Updating GamesSince to reflect new stats' timelines for yerterday, {}".format(myDate))

    #Load in GamesSince from the previous day, which will be copied and updated
    GamesSince = pd.read_pickle('dailyGamesSince/dailyGamesSince_{}.pickle'.format(myDate - datetime.timedelta(days=1))).copy()

    #Load my_games_clean dictionary
    my_games_clean = pd.read_pickle('dailyGamesClean/dailyGamesClean_{}.pickle'.format(myDate))
    
    #Set columns to iterate through
    cols = ['G', 'A', 'PTS', 'PIM', 'EV', 'PP', 'SH', 'GW', 'S']

    #Also add in last times the player was + or -
    pmCols = ['+', '-']

    #Iterate through all games in my_games_clean dictionary
    for index, game_df in my_games_clean.items():

        #Create the new index, which is a union of the main one and the one from the specific game
        new_index = GamesSince.index.union(game_df.index)
        #Implement the new index, filling in empty values with the value 0
        GamesSince = GamesSince.reindex(new_index, fill_value=0)

        #Iterate through columns to 1 - reset counter to 0 for any stat change and 2 - increment counters for unchanged stats by 1
        for column in cols:
            GamesSince.loc[game_df[game_df[column] > 0].index, column] = 0
            GamesSince.loc[game_df[game_df[column] == 0].index, column] += 1

        #Increment all players' Total Recorded Games by 1
        GamesSince.loc[game_df.index, 'Total Recorded Games'] += 1

        #Iterate through columns to edit +/- columns
        for column in pmCols:
            if column == '+':
                GamesSince.loc[game_df[game_df['+/-'] > 0].index, column] = 0
                GamesSince.loc[game_df[game_df['+/-'] <= 0].index, column] += 1
            elif column == '-':
                GamesSince.loc[game_df[game_df['+/-'] < 0].index, column] = 0
                GamesSince.loc[game_df[game_df['+/-'] >= 0].index, column] += 1

    #Save GamesSince
    savePickle(GamesSince, 'dailyGamesSince/dailyGamesSince_{}'.format(myDate))

    print('Finished updating GamesSince for {}'.format(myDate))

def incorporateSpecificDaysStats(date='2000-1-1'):

    myDate = pd.to_datetime(date, format='%Y-%m-%d')

    #Instantiate my_games_clean
    my_games_clean = pd.read_pickle('dailyGamesClean/dailyGamesClean_{}.pickle'.format(myDate))

    print('Adding {} games to my_df'.format(len(my_games_clean)))

    #Load in the day befores my_df
    my_df = pd.read_pickle('dailyMyDF/dailyMyDF_{}.pickle'.format(myDate - datetime.timedelta(days=1)))

    #Create main df for all day's games
    new_df = pd.concat([game for game in my_games_clean.values()])
    new_df = my_df.groupby(my_df.index).sum()

    #Combine my_df and new_df
    my_df = my_df.add(new_df, fill_value=0)

    # Convert columns to int
    columns_to_int = ['G', 'A', 'PTS', '+/-', 'PIM', 'EV', 'PP', 'SH', 'GW', 'EV', 'PP', 'SH', 'S', 'Shifts']
    for column in columns_to_int:
        if column in my_df.columns:
            my_df[column] = my_df[column].astype(int)

    savePickle(my_df, 'dailyMyDF/dailyMyDF_{}'.format(myDate))

