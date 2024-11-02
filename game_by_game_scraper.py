import pandas as pd
from curl_cffi import requests as cureq
from sidearm_scraper import Sidearm_Scraper
import re


def fetch_tables(url_passed: str):
    # Fetch data and parse tables
    response = cureq.get(url_passed, impersonate="chrome")
    tables_found = pd.read_html(response.content)
    away_team_table = tables_found[1]
    home_team_table = tables_found[4]

    # Mapping table
    mapping_table = {
        'MIN': 'MP',
        'PTS': 'PTS',
        'A': 'AST',
        'ORB-DRB': ('OREB', 'DREB'),  # Split into Offensive and Defensive Rebounds
        'REB': 'REB',
        'FG': ('FGM', 'FGA'),  # Split into Made and Attempted Field Goals
        'FT': ('FTM', 'FTA'),  # Split into Made and Attempted Free Throws
        'BLK': 'BLK',
        'STL': 'STL',
        'TO': 'TOV',
        'PF': 'FOUL',
        '3PT': ('THREES', '3PTA'),  # Split into Made and Attempted Three-Pointers
    }
    """        PD Print Out        
        ##                       02
        Player     02 Frericks,Beau
        GS                        *
        MIN                      37
        FG                     5-12
        3PT                     3-8
        FT                      4-5
        ORB-DRB                 0-3
        REB                       3
        PF                        1
        A                         4
        TO                        1
        BLK                       0
        STL                       2
        PTS                      17
    """

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

    def clean_name(name):
        # Remove any leading numbers and spaces
        name = re.sub(r"^\d+\s*", "", name)

        # Match "Last Suffix, First" or "Last, First Suffix" format
        match = re.match(r"^([\w'\-]+(?:\s+(?:Jr\.|III|II|Sr\.))?),\s*([\w\-]+)$", name)
        if match:
            last_name_with_suffix, first_name = match.groups()
            # Split the last name and suffix if suffix is present
            if " " in last_name_with_suffix:
                last_name, suffix = last_name_with_suffix.rsplit(" ", 1)
                return f"{first_name} {last_name} {suffix}"
            else:
                last_name = last_name_with_suffix
                return f"{first_name} {last_name}"

        # If no match, assume name is already in "First Last" format
        return name

    all_players_data = {}
    exclusions = ['TM TEAM', 'Totals']

    # Process each table (away and home)
    for i, table in enumerate([away_team_table, home_team_table]):
        if i == 0:
            team_name = 'AWAY'
        else:
            team_name = 'HOME'

        for _, row in table.iterrows():
            player_name = row.get('Player', '').strip()

            if player_name not in exclusions:
                cleaned_name = clean_name(player_name)
                if cleaned_name not in all_players_data:
                    all_players_data[cleaned_name] = {'PLAYER': cleaned_name}

                # Add team name to the player's data
                all_players_data[cleaned_name]['Team'] = team_name

                # Process each column in the row
                for column_name in row.index:
                    mapped_attr = mapping_table.get(column_name)
                    cell_value = row[column_name]

                    if mapped_attr:
                        if isinstance(mapped_attr, tuple):  # Split stats (e.g., "5-12" for FG)
                            split_values = cell_value.split('-')
                            if len(split_values) == 2:
                                all_players_data[cleaned_name][mapped_attr[0]] = convert_to_numeric(split_values[0])
                                all_players_data[cleaned_name][mapped_attr[1]] = convert_to_numeric(split_values[1])
                        else:
                            all_players_data[cleaned_name][mapped_attr] = convert_to_numeric(cell_value)

    return all_players_data


if __name__ == '__main__':
    odu_url = "https://ohiodominicanpanthers.com/sports/mens-basketball/stats/"
    odu_url_partial = "https://ohiodominicanpanthers.com"
    hillsdale_url = "https://hillsdalechargers.com/sports/mens-basketball/stats/"
    hillsdale_url_partial = "https://hillsdalechargers.com"

    season = "2023-24"
    team_name = "Ohio Dominican University"
    url = odu_url
    scraper = Sidearm_Scraper(url=url)
    scraper.fetch_page()
    scraper.extract_article_content()
    scraper.extract_partial_url()
    game_url_list = scraper.extract_game_urls()
    url_one = game_url_list[0]
    print(url_one)
    players_cleaned = fetch_tables(url_one)
    print(players_cleaned)
