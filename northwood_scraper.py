from curl_cffi import requests as cureq
import pandas as pd
from model.player import Player
import re


def northwood_scraper(url: str, season: str):
    # Combine URL, season, and Northwood URL extension
    url = f"{url}{season}/teams/northwood?view=lineup"
    response = cureq.get(url, impersonate="chrome")

    tables_created = pd.read_html(response.content)

    # Define column mappings for Northwood data
    mapping_table_1 = {
        'Name': 'PLAYER',
        'min': 'MP',
        'pts': 'PTS',
        'fg': 'FGM',  # FGM to be split
        'pct': 'FGP',
        '3pt': 'THREES',  # THREES to be split
        'ft': 'FTM',  # FTM to be split
        'pct.2': 'FTP',
        'fga': 'FGA',  # FGA separately assigned
    }

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

    all_players_data = {}
    exclusions = ['Totals', 'Opponent']

    def convert_to_numeric(value):
        """Convert value to int or float if possible, else return 0 for missing or '-' values."""
        if value == '-':
            return 0
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except (ValueError, TypeError):
            return value  # Return as-is if conversion fails

    def extract_stats(row_data):
        """Extract stats and clean names, if needed."""
        stats_dict = {}
        # Extract FGM/FGA, FTM/FTA, THREES
        if 'fg' in row_data:
            fgm_fga = row_data['fg'].split('-')
            stats_dict['FGM'] = convert_to_numeric(fgm_fga[0]) if len(fgm_fga) > 1 else None
            stats_dict['FGA'] = convert_to_numeric(fgm_fga[1]) if len(fgm_fga) > 1 else None
        if 'ft' in row_data:
            ft_fta = row_data['ft'].split('-')
            stats_dict['FTM'] = convert_to_numeric(ft_fta[0]) if len(ft_fta) > 1 else None
            stats_dict['FTA'] = convert_to_numeric(ft_fta[1]) if len(ft_fta) > 1 else None
        if '3pt' in row_data:
            threes = row_data['3pt'].split('-')
            stats_dict['THREES'] = convert_to_numeric(threes[0]) if len(threes) > 1 else None

        return stats_dict

    # Loop through tables
    for i, mapping in zip([5, 6], [mapping_table_1, mapping_table_2]):
        table = tables_created[i]

        for _, row in table.iterrows():
            player_name = row.get('Name', '').strip()
            if player_name and player_name not in exclusions:

                if player_name not in all_players_data:
                    all_players_data[player_name] = {'PLAYER': player_name}

                stats = extract_stats(row)
                all_players_data[player_name].update(stats)
                for column_name, attribute in mapping.items():
                    if column_name in row and attribute not in stats:
                        all_players_data[player_name][attribute] = convert_to_numeric(row[column_name])

    return all_players_data


if __name__ == '__main__':

    # Test and process player data
    url = "https://www.gonorthwood.com/sports/mbkb/"
    season = "2023-24"
    players_list = []
    scraper = northwood_scraper(url=url, season=season)

    for name, data in scraper.items():
        # Clean and assign data in Player instantiation
        cleaned_name = re.sub(r'\s+', ' ', data['PLAYER']).strip()
        data['PLAYER'] = cleaned_name
        print(f"Final Cleaned Name Passed to Player: '{cleaned_name}'")  # Debugging line
        new_player = Player(data=data, team="Northwood", conference=True)
        players_list.append(new_player)

    # Output player information
    for player in players_list:
        print(f"Player Name: {player.PLAYER}")
        print(f"Team: {player.TEAM}")
        print(f"Minutes Played: {player.MP} ({type(player.MP)})")
        print(f"Points: {player.PTS} ({type(player.PTS)})")
        print(f"Assists: {player.AST} ({type(player.AST)})")
        print(f"Rebounds: {player.REB} ({type(player.REB)})")
        print(f"Steals: {player.STL} ({type(player.STL)})")
        print(f"Turnovers: {player.TOV} ({type(player.TOV)})")
        print(f"Personal Fouls: {player.FOUL} ({type(player.FOUL)})")
        print("-" * 40)
