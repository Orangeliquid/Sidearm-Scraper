from sidearm_data import Sidearm_Data

"""
stats needed:
CONFERENCE: bool
MP(Called Minutes TOT in json):
PTS(Called Scoring PTS in json):
AST:
OREB(Called Rebounds OFF in json):
REB(Called Rebounds TOT in json):
FGM:
FGA(Called FG TOTAL in excel):
FG%(Calling FGP in class:
FTM:
FTA(Called FT TOTAL in excel):
FT%(Called FTP in class:
BLK:
STL:
TOV:
FOUL(Called PF in json):
3P(Called 3PT in json):
"""


class Player:
    def __init__(self, data: dict, team: str, conference: bool):
        self.TEAM = team
        self.CONFERENCE = conference
        self.PLAYER = None
        self.MP = None  # Minutes Played
        self.PTS = None  # Points
        self.AST = None  # Assists
        self.OREB = None  # Offensive Rebounds
        self.REB = None  # Total Rebounds
        self.FGM = None  # Field Goals Made
        self.FGA = None  # Field Goals Attempted
        self.FGP = None  # Field Goal Percentage
        self.FTM = None  # Free Throws Made
        self.FTA = None  # Free Throws Attempted
        self.FTP = None  # Free Throw Percentage
        self.BLK = None  # Blocks
        self.STL = None  # Steals
        self.TOV = None  # Turnovers
        self.FOUL = None  # Personal Fouls
        self.THREES = None  # 3PT Field Goals Made
        self.UPER = None
        self.PER = None

        # Call the attribute setter to populate values from the data dictionary
        self.attribute_setter(data)

    def attribute_setter(self, data: dict):
        # Map dictionary keys to class attributes
        mapping = {
            'Player Player': 'PLAYER',
            'Minutes TOT': 'MP',
            'Scoring PTS': 'PTS',
            'AST AST': 'AST',
            'Rebounds OFF': 'OREB',
            'Rebounds TOT': 'REB',
            'FG FGM': 'FGM',
            'FG FGA': 'FGA',
            'FG FG%': 'FGP',
            'FT FTM': 'FTM',
            'FT FTA': 'FTA',
            'FT FT%': 'FTP',
            'BLK BLK': 'BLK',
            'STL STL': 'STL',
            'TO TO': 'TOV',
            'PF PF': 'FOUL',
            '3PT 3PT': 'THREES',
        }

        # Loop through the mapping and set the attributes
        for key, attr in mapping.items():
            if key in data:
                setattr(self, attr, data[key])

        # Clean self.PLAYER to fit excel formatting
        if self.PLAYER:
            split_name = self.PLAYER.split()[:2]
            first_name = split_name[1]
            last_name = split_name[0].split(",")[0]
            self.PLAYER = f"{first_name} {last_name}"


# -----------------------------------------------------------------------------------------------------------------
# team_name = "Ohio Dominican University"
# url = f"https://ohiodominicanpanthers.com/sports/mens-basketball/stats/"
#
# scraper = Sidearm_Data(team=team_name, url=url, year=season, create_json=False)
# overall_lvl = scraper.tables_data['Overall']
#
# # Loop through players excluding "TEAM", "TOTAL", "OPPONENTS"
# for tag in overall_lvl[:-3]:
#     new_player = Player(tag, team_name)
#     players_list.append(new_player)  # Append each player to the list
#     print(new_player.PLAYER)  # Print the player's name to verify
#
# # Now players_list contains all Player instances
# for player in players_list:
#     print(f"Player Name: {player.PLAYER}")
#     print(f"Team: {player.TEAM}")
#     print(f"Minutes Played: {player.MP}")
#     print(f"Points: {player.PTS}")
#     print(f"Assists: {player.AST}")
#     print(f"Rebounds: {player.REB}")
#     print(f"Steals: {player.STL}")
#     print(f"Turnovers: {player.TOV}")
#     print(f"Personal Fouls: {player.FOUL}")
#     print("-" * 40)  # Separator between players for readability
