"""

In this file I'll establish my classes for NHL teams, players, etc

"""

class NHL_Team(object):
    def __init__(self, name=None, coach=None):
        self.name = name
        self.members = []
        self.coach = coach

class person(object):
    def __init__(self, name=None, title=None):
        """
        Class defining each person. This could be a coach, player, anything.
        Arguments:
        name {[string]} -- [person's name, first and last. Ex: 'Steven Stamkos']
        title {[string]} -- [person's title. Ex: 'Player']
        """
        self.name = name
        self.title = title

    def __str__(self):
        # return 'Player Name: ', self.name, '\tTeam:', self.team, 'Position:', self.position
        return self.name

class hockey_player(person):
    # Initiate a player number that will be unique to each player and will be ascribed to them at creation
    player_number = 1

    def __init__(self, name=None, title=None, position=None, team=None):
        person.__init__(self, name)
        self.position = position
        self.team = team
        self.title = title
        self.player_number = hockey_player.player_number
        hockey_player.player_number += 1
        # Update the below stats_dataframe to host stats for each player. Should I do this or keep the stats solely within the dataframe, my_data?
        self.stats_dataframe = None

a = hockey_player('Jonathan Olson')