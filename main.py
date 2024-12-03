
"""
- create class Player and set class vars to stats
- loop through all url and collect all individual stats
- get all players into object - add that to list 
- do this for all players in conference
- place in list
- look to format for excell
- use overall player stats

stats needed:
CONFERENCE: bool
MP(Called Minutes TOT in json):
PTS(Called Scoring PTS in json):
AST:
OREB(Called Rebounds OFF in json):
REB(Called Rebounds TOT in json):
FGM:
FGA(Called FG TOTAL in excel):
FG%:
FTM:
FTA(Called FT TOTAL in excel):
FT%:
BLK:
STL:
TOV:
FOUL(Called PF in json):
3P(Called 3PT in json):

- get game by game later from each conference team's url
"""

# -------------------------------------------------------------------------------------
from sidearm_data import Sidearm_Data
from game_by_game_scraper import fetch_tables, determine_home_away, clean_title, determine_conference
from sidearm_scraper import Sidearm_Scraper
from model.player import Player
from util.per_util import calculate_pers
import season_sheets_post
import game_sheets_post
import time


def post_game_data(game_number):
    odu_url = "https://ohiodominicanpanthers.com/sports/mens-basketball/stats/"
    season = "2024-25"
    team_name = "Ohio Dominican University"
    url = odu_url
    scraper = Sidearm_Scraper(url=url)
    scraper.fetch_page()
    scraper.extract_article_content()
    scraper.extract_partial_url()
    game_url_list = scraper.extract_game_urls()
    try:
        requested_url = game_url_list[game_number]
    except IndexError:
        raise IndexError(
            f"Game number {game_number} is out of range. Valid range is 0 to {len(game_url_list) - 1}."
        )
    players_cleaned = fetch_tables(requested_url)
    # determine home or away so player data can be sorted to only odu
    odu_home_away = determine_home_away(players_cleaned)
    cleaned_title, away_team_full, home_team_full, away_team_strip, home_team_strip = clean_title(players_cleaned)
    conference_game = determine_conference(home_team_strip, away_team_strip)

    players_list = []
    for player in players_cleaned:
        new_player = Player(players_cleaned[player], cleaned_title, True)
        players_list.append(new_player)

    calculate_pers(players_list)

    home_team_list = [player for player in players_list if player.TEAM == "HOME"]
    away_team_list = [player for player in players_list if player.TEAM == "AWAY"]

    game_sheets_post.post_season_stats(home_data=home_team_list,
                                       away_data=away_team_list,
                                       title=cleaned_title,
                                       away=away_team_strip,
                                       home=home_team_strip)


# 0 indexed - all done - hitting write limit after 2 games posted
# games = [5]
# for i in games:
#     post_game_data(i)
#     time.sleep(60)

# penn beaver was last game
post_game_data(-1)


def post_season_data():
    team_name = "Ohio Dominican"
    url = f"https://ohiodominicanpanthers.com/sports/mens-basketball/stats/"
    season = "2024-25"

    scraper = Sidearm_Data(team=team_name, url=url, year=season, create_json=False)
    overall_lvl = scraper.tables_data['Overall']
    players_list = []

    # Loop through players excluding "TEAM", "TOTAL", "OPPONENTS"
    for tag in overall_lvl[:-3]:
        new_player = Player(tag, team_name, True)
        players_list.append(new_player)  # Append each player to the list
        # print(new_player.PLAYER)  # Print the player's name to verify

    # Now players_list contains all Player instances
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

    calculate_pers(players_list)
    print(players_list)
    # output_list = ["Ohio Dominican"]
    # for player in players_list:
    #     if player.TEAM in output_list:
    #         print(f"Player: {player.PLAYER} | Team: {player.TEAM} | PER: {player.PER} | HAS_PLAYED: {player.HAS_PLAYED}")
    # for player in players_list:
    #     for var, val in player.__dict__.items():
    #         print(f"{var}: {val}")

    # post_headers()
    # post_player_data(players_list)
    season_sheets_post.post_season_stats(players_list)


# call function to post current team stats throughout 2024-25 so far
# post_season_data()
