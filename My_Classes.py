"""

In this file I'll establish my classes for NHL teams, players, etc

"""

class NHL_Team(object):
    def __init__(self, Name=None, Coach=None, Abbreviation=None):
        self.Name = Name
        self.Members = []
        self.Coach = Coach
        self.Abbreviation = Abbreviation

class person(object):
    def __init__(self, Name, Title=None):
        """
        Class defining each person. This could be a coach, player, anything.
        Arguments:
        name {[string]} -- [person's name, first and last. Ex: 'Steven Stamkos']
        title {[string]} -- [person's title. Ex: 'Player']
        """
        self.Name = Name
        self.Title = Title

    def __str__(self):
        # return 'Player Name: ', self.name, '\tTeam:', self.team, 'Position:', self.position
        return self.Name

class hockey_player(person):
    # Initiate a player number that will be unique to each player and will be ascribed to them at creation
    player_number = 1

    def __init__(self, Number, Name, Team, Nationality, Position, Age, Height, Weight, Handedness, Birth_Date, Salary, Draft):
        person.__init__(self, Name)
        self.Number = Number
        self.Team = Team
        self.Nationality = Nationality
        self.Position = Position
        self.Age = Age
        self.Height = Height
        self.Weight = Weight
        self.Handedness = Handedness
        self.Birth_Date = Birth_Date
        self.Salary = Salary
        self.Draft = Draft


class LengthException(Exception):
    """ Exception used when moving game dfs from my_games_clean to the permament storage dict, all_time_clean_games"""
    pass

