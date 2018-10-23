
from My_Classes import NHL_Team, hockey_player
from game_by_game_scrape import savePickle
import pandas as pd

SJS = NHL_Team(Name='San Jose Sharks', Coach='Peter deBoer', Abbreviation='SJS')
TOR = NHL_Team(Name='Toronto Maple Leafs', Coach='Mike Babcock', Abbreviation='TOR')
VAN = NHL_Team(Name='Vancouver Canucks', Coach='Travis Green', Abbreviation='VAN')
WSH = NHL_Team(Name='Washington Capitals', Coach='Todd Reirden', Abbreviation='WSH')
BUF = NHL_Team(Name='Buffalo Sabres', Coach='Phil Housley', Abbreviation='BUF')
CAR = NHL_Team(Name='Carolina Hurricanes', Coach="Rod Brind'Amour", Abbreviation='CAR')
COL = NHL_Team(Name='Colorado Avalanche', Coach='Jared Bednar', Abbreviation='COL')
DAL = NHL_Team(Name='Dallas Stars', Coach='Jim Montgomery', Abbreviation='DAL')
DET = NHL_Team(Name='Detroit Redwings', Coach='Jeff Blashill', Abbreviation='DET')
NYR = NHL_Team(Name='New York Rangers', Coach='David Quinn', Abbreviation='NYR')
OTT = NHL_Team(Name='Ottawa Senators', Coach='Guy Boucher', Abbreviation='OTT')
PIT = NHL_Team(Name='Pittsburgh Penguins', Coach='Mike Sullivan', Abbreviation='PIT')
STL = NHL_Team(Name='St. Louis Blues', Coach='Mike Yeo', Abbreviation='STL')
VEG = NHL_Team(Name='Vegas Golden Knights', Coach='Gerard Gallant', Abbreviation='VEG')
CBJ = NHL_Team(Name='Columbus Blue Jackets', Coach='John Tortorella', Abbreviation='CBJ')
LAK = NHL_Team(Name='Los Angeles Kings', Coach='John Stevens', Abbreviation='LAK')
ARI = NHL_Team(Name='Arizona Coyotes', Coach='Rick Tocchet', Abbreviation='ARI')
CGY = NHL_Team(Name='Calgary Flames', Coach='Bill Peters', Abbreviation='CGY')
MIN = NHL_Team(Name='Minnesota Wild', Coach='Bruce Boudreau', Abbreviation='MIN')
NJD = NHL_Team(Name='New Jersey Devils', Coach='John Hynes', Abbreviation='NJD')
NYI = NHL_Team(Name='New York Islanders', Coach='Barry Trotz', Abbreviation='NYI')
TBL = NHL_Team(Name='Tampa Bay Lightning', Coach='John Cooper', Abbreviation='TBL')
CHI = NHL_Team(Name='Chicago Blackhawks', Coach='Joel Quenneville', Abbreviation='CHI')
ANA = NHL_Team(Name='Anaheim Ducks', Coach='Randy Carlyle', Abbreviation='ANA')
BOS = NHL_Team(Name='Boston Bruins', Coach='Bruce Cassidy', Abbreviation='BOS')
NSH = NHL_Team(Name='Nashville Predators', Coach='Peter Laviolette', Abbreviation='NSH')
PHI = NHL_Team(Name='Philadelphia Flyers', Coach='Dave Hakstol', Abbreviation='PHI')
WPG = NHL_Team(Name='Winnipeg Jets', Coach='Paul Maurice', Abbreviation='WPG')
FLA = NHL_Team(Name='Florida Panthers', Coach='Bob Boughner', Abbreviation='FLA')
MTL = NHL_Team(Name='Montreal Canadiens', Coach='Claude Julien', Abbreviation='MTL')
EDM = NHL_Team(Name='Edmonton Oilers', Coach='Todd McLellan', Abbreviation='EDM')

my_teams = [SJS, TOR, VAN, WSH, BUF, CAR, COL, DAL, DET, NYR, OTT, PIT, STL, 
VEG, CBJ, LAK, ARI, CGY, MIN, NJD, NYI, TBL, CHI, ANA, BOS, NSH, PHI, WPG, 
FLA, MTL, EDM]


#Initialize dict of team names (string - keys) and players (hockey_player instances in a list - values)
NHL_teams_and_players = {}

#Loop through teams, creating a hockey_player instance for each player on that team, adding it to the NHL_teams_and_players dictionary
for team in my_teams:
    print('Team Name:', team.Name)
    #Create the team's URL
    url = "https://www.hockey-reference.com/teams/{}/2019.html".format(team.Abbreviation)
    my_df_list = pd.read_html(url)
    #Select for the correct table
    my_dfs = []
    for df in my_df_list:
        if df.columns[0] == 'No.':
            my_dfs.append(df)
    my_df = my_dfs[0].copy()
    my_df = my_df.iloc[:-1, :]
    #Clean the table
    my_df = my_df[['No.', 'Player', 'Flag', 'Pos', 'Age', 'Ht', 'Wt', 'S/C', 'Birth Date', 'Salary', 'Draft']]
    my_df.columns = ['Number', 'Name', 'Nationality', 'Position', 'Age', 'Height', 'Weight', 'Handedness', 'Birth Date', 'Salary', 'Draft']
    my_df['Nationality'] = my_df['Nationality'].str.upper()
    my_df['Handedness'] = my_df['Handedness'].str.replace('[^a-zA-Z]', '')
 
    #Create a new key-value pair, for the current team
    NHL_teams_and_players[team.Name] = []

    #Create and add players to this new key-value pair
    for i in range(len(my_df)):
        row = my_df.iloc[i, :]

        #Create player instance
        my_player = hockey_player(
            Number = row['Number'], 
            Name = row['Name'], 
            Team = team.Name, 
            Nationality = row['Nationality'], 
            Position = row['Position'], 
            Age = row['Age'], 
            Height = row['Height'], 
            Weight = row['Weight'], 
            Handedness = row['Handedness'], 
            Birth_Date = row['Birth Date'], 
            Salary = row['Salary'], 
            Draft = row['Draft']
            )

        #Add player to key-value pair
        NHL_teams_and_players[team.Name].append(my_player)

# NHL_teams_and_players[list(NHL_teams_and_players.keys())[21]]

#Save each team as a pickle file
for team in my_teams:
    savePickle(team, team.Name)

#Save my list of team names
savePickle(my_teams, 'my_teams')

#Save NHL_teams_and_players dataframe as pickle
savePickle(NHL_teams_and_players, 'NHL_teams_and_players')