from curl_cffi import requests as cureq
import pandas as pd
from model.player import Player
import re

"""
mapping = {
            'Name': 'PLAYER',
            'min': 'MP',
            'pts': 'PTS',
            'ast': 'AST',
            'off': 'OREB',
            'reb': 'REB',
            'fgm': 'FGM',
            'fga': 'FGA',
            'fgp': 'FGP',
            'ftm': 'FTM',
            'fta': 'FTA',
            'ftp': 'FTP',
            'blk': 'BLK',
            'stl': 'STL',
            'to': 'TOV',
            'pf': 'FOUL',
            '3pt': 'THREES',
        }
"""


def northwood_scraper(url: str, season: str):
    url = f"{url}{season}/teams/northwood?view=lineup"
    response = cureq.get(url, impersonate="chrome")

    tables_created = pd.read_html(response.content)

    # Define the column mappings for Northwood data
    # Table 6 - Lineup/Shooting
    mapping_table_1 = {
        'Name': 'PLAYER',
        'min': 'MP',
        'pts': 'PTS',
        'fg': 'FGM',  # FGM to be split
        'pct': 'FGP',
        '3pt': 'THREES',  # THREES to be split (only the made part is used)
        'ft': 'FTM',  # FTM to be split
        'pct.2': 'FTP',
        'fga': 'FGA',  # FGA will be assigned separately
    }

    # Table 7 - Lineup/Ball control
    mapping_table_2 = {
        'Name': 'PLAYER',
        'min': 'MP',
        'ast': 'AST',
        'off': 'OREB',
        'reb': 'REB',
        'blk': 'BLK',
        'stl': 'STL',
        'to': 'TOV',
        'pf': 'FOUL',
    }

    # Store all players' data from both tables 6 and 7
    all_players_data = {}
    exclusions = ['Totals', 'Opponent']

    def extract_stats(row_data):
        """Extract and return statistics for FGM, FGA, FTM, FTA, and THREES from the row."""
        stats_dict = {}

        # FGM and FGA
        if 'fg' in row_data:
            fgm_fga = row_data['fg'].split('-') if '-' in row_data['fg'] else [row_data['fg'], None]
            stats_dict['FGM'] = int(fgm_fga[0])  # Made
            stats_dict['FGA'] = int(fgm_fga[1]) if fgm_fga[1] is not None else None  # Attempted

        # FTM and FTA
        if 'ft' in row_data:
            ft_fta = row_data['ft'].split('-') if '-' in row_data['ft'] else [row_data['ft'], None]
            stats_dict['FTM'] = int(ft_fta[0])  # Made
            stats_dict['FTA'] = int(ft_fta[1]) if ft_fta[1] is not None else None  # Attempted

        # THREES
        if '3pt' in row_data:
            threes = row_data['3pt'].split('-') if '-' in row_data['3pt'] else [row_data['3pt'], None]
            stats_dict['THREES'] = int(threes[0])  # Made, no need for attempts here

        return stats_dict

    # Loop through tables 6 and 7 (indexes 5 and 6)
    for i, mapping in zip([5, 6], [mapping_table_1, mapping_table_2]):
        table = tables_created[i]

        # Loop through each row (each player's data) in the table
        for _, row in table.iterrows():
            player_name = row.get('Name', '').strip()  # Get player name and strip whitespace

            # Exclude non-player rows
            if player_name not in exclusions:
                player_name = re.sub(r'\s+', ' ', player_name).strip()  # Replace multiple spaces and trim

                print(f"Cleaned Player Name: '{player_name}'")
                # If player does not exist in the dictionary, initialize it
                if player_name not in all_players_data:
                    all_players_data[player_name] = {'PLAYER': player_name}

                # Extract stats and map them
                stats = extract_stats(row)
                all_players_data[player_name].update(stats)

                # Map other attributes
                for column_name, attribute in mapping.items():
                    if column_name in row and attribute not in stats:
                        all_players_data[player_name][attribute] = row[column_name]

    return all_players_data

# Todo Fix player.Player from having extra whitespace in name
url = "https://www.gonorthwood.com/sports/mbkb/"
season = "2023-24"
players_list = []
scraper = northwood_scraper(url=url, season=season)
for name in scraper:
    data = scraper[name]
    new_player = Player(data=data, team="Northwood", conference=True)
    players_list.append(new_player)

for player in players_list:
    print(f"Player Name: {player.PLAYER}")
    print(f"Team: {player.TEAM}")
    print(f"Minutes Played: {player.MP}")
    print(f"Points: {player.PTS}")
    print(f"Assists: {player.AST}")
    print(f"Rebounds: {player.REB}")
    print(f"Steals: {player.STL}")
    print(f"Turnovers: {player.TOV}")
    print(f"Personal Fouls: {player.FOUL}")
    print("-" * 40)