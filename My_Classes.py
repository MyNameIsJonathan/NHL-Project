"""

In this file I'll establish my classes for NHL teams, players, etc

"""

class NHL_Team(object):
    def __init__(self, name=None):
        self.name = name
        self.members = []

class person(object):
    def __init__(self, name=None):
        self.name = name

class hockey_player(person):
    # Initiate a player number that will be unique to each player and will be ascribed to them at creation
    player_number = 1

    def __init__(self, name=None, position=None, team=None):
        person.__init__(self, name)
        self.position = position
        self.team = team
        self.player_number = hockey_player.player_number
        hockey_player.player_number += 1
        self.stats_dataframe = None

