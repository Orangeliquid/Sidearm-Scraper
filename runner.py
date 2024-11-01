from model.player import Player
from sidearm_data import Sidearm_Data
from util.constants import TEAMS
from util.per_util import calculate_pers
from northwood_scraper import northwood_scraper
import re


# set season to desired season to get data
season = "2023-24"

# Create a list to store all Player instances
players_list = []

print(TEAMS)

# iterate through TEAMS tuples
for team in TEAMS:
    # add conditional if source is "Sidearm"
    if team.source == "Sidearm":
        # set a list to filter out rows we don't want
        exclusions = ["Team  TM Team", "Total", "Opponents"]
        scraper = Sidearm_Data(team=team.name, url=team.url, year=season, create_json=False)
        overall_lvl = scraper.tables_data['Overall']

        # Loop through players excluding "TEAM", "TOTAL", "OPPONENTS"
        for tag in overall_lvl:
            if tag['Player Player'] not in exclusions:
                new_player = Player(tag, team.name, team.is_conference)
                players_list.append(new_player)  # Append each player to the list
                print(f"NEW PLAYER: {new_player.PLAYER}")  # Print the player's name to verify
                # print(f"self.HAS_PLAYED: {new_player.HAS_PLAYED}")
        print("-" * 40)

    elif team.source == "Northwood":
        scraper = northwood_scraper(url=team.url, season=season)

        for name, data in scraper.items():
            # Clean and assign data in Player instantiation
            cleaned_name = re.sub(r'\s+', ' ', data['PLAYER']).strip()
            data['PLAYER'] = cleaned_name
            new_player = Player(data=data, team="Northwood", conference=True)
            players_list.append(new_player)


print(len(players_list))  # 239 total player obj created from 16 links in team_urls

# TODO: Filter out players with 0 minutes?
calculate_pers(players_list)
output_list = ["Ohio Dominican", "Northwood"]
for player in players_list:
    if player.TEAM in output_list:
        print(f"Player: {player.PLAYER} | Team: {player.TEAM} | PER: {player.PER} | HAS_PLAYED: {player.HAS_PLAYED}")

# Check to see how many player have not played at least 1 minute
# count = 0
# for player in players_list:
#     if not player.HAS_PLAYED:
#         count += 1
# print(count)
