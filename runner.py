from model.player import Player
from sidearm_data import Sidearm_Data
from util.constants import TEAMS
from util.per_util import calcuate_pers


# set season to desired season to get data
season = "2023-24"

# set a list to filter out rows we don't want
exclusions = ["Team  TM Team", "Total", "Opponents"]

# Create a list to store all Player instances
players_list = []

print(TEAMS)

# iterate through team_urls_keys
for team in TEAMS:
    scraper = Sidearm_Data(team=team.name, url=team.url, year=season, create_json=False)
    overall_lvl = scraper.tables_data['Overall']

    # Loop through players excluding "TEAM", "TOTAL", "OPPONENTS"
    for tag in overall_lvl:
        if tag['Player Player'] not in exclusions:
            new_player = Player(tag, team.name, team.is_conference)
            players_list.append(new_player)  # Append each player to the list
            print(f"NEW PLAYER: {new_player.PLAYER}")  # Print the player's name to verify
    print("-" * 40)

print(len(players_list))  # 224 total player obj created from 15 links in team_urls

# TODO: Filter out players with 0 minutes?
calcuate_pers(players_list)

for player in players_list:
    if player.TEAM == "Ohio Dominican":
        print(f"Player: {player.PLAYER} Team: {player.TEAM} PER: {player.PER}")
