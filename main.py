from sidearm_data import Sidearm_Data
from cleaner import (
    clean_team_data,
    clean_individual_data,
    clean_game_by_game_data,
    clean_game_highs_data,
    clean_category_leaders_data,
)

# Northwood is the only missing conference team that does not follow sidearm html structure
# all that needs changed is the season below, following the current format
odu_url = f"https://ohiodominicanpanthers.com/sports/mens-basketball/stats/"
hillsdale_url = f"https://hillsdalechargers.com/sports/mens-basketball/stats/"
# need Northwood
findlay_url = f"https://findlayoilers.com/sports/mens-basketball/stats/"
thomas_moore = f"https://thomasmoresaints.com/sports/mens-basketball/stats/"
tiffin_url = f"https://gotiffindragons.com/sports/mens-basketball/stats/"
malone_url = f"https://malonepioneers.com/sports/mens-basketball/stats/"
kentucky_wesleyan_url = f"https://tnutrojans.com/sports/mens-basketball/stats/"
ashland_url = f"https://goashlandeagles.com/sports/mens-basketball/stats/"
cedarville_url = f"https://yellowjackets.cedarville.edu/sports/mens-basketball/stats/"
lake_erie_url = f"https://lakeeriestorm.com/sports/mens-basketball/stats/"
walsh_url = f"https://athletics.walsh.edu/sports/mens-basketball/stats/"

central_state = f"https://maraudersports.com/sports/mens-basketball/stats/"  # not conference
missouri_s_and_t_url = f"https://minerathletics.com/sports/mens-basketball/stats/"  # not conference
roosevelt_url = f"https://rooseveltlakers.com/sports/mens-basketball/stats/"  # not conference
lincoln_url = f"https://lubluetigers.com/sports/mens-basketball/stats/"  # not conference

# follow these variables as an example to plug in new teams
season = "2023-24"
team_name = "Hillsdale University"
url = hillsdale_url

# Use scraper to grab a_tags and category headers
scraper = Sidearm_Data(team=team_name, url=url, year=season, create_json=True)
original_json_created = scraper.new_file_name

# first category to clean - targeting TEAM category
modified_json = clean_team_data(original_json_created)

# second category to clean - targeting INDIVIDUAL category
clean_individual_data(modified_json)

# third category to clean - targeting GAME-BY-GAME category
clean_game_by_game_data(modified_json)

# fourth category to clean - targeting GAME HIGHS category
clean_game_highs_data(modified_json)

# fifth and final category to clean - targeting CATEGORY LEADERS category
clean_category_leaders_data(modified_json)

# -------------------------------------------------------------------------------------
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
# season = "2023-24"
# odu_url = f"https://ohiodominicanpanthers.com/sports/mens-basketball/stats/{season}"
# scraper = ODU_Scraper(odu_url)
# scraper.fetch_page()
# scraped_soup = scraper.soup
#
# scraper.extract_article_content()
# scraped_article = scraper.article_content
#
# article_title = scraper.get_article_title()
# print(scraper.article_title)
#
# categories = scraper.get_category_titles()
# print(categories)
#
# a_tags = scraper.get_a_tags()
# print(a_tags)
#
# table_data = scraper.get_table_titles_and_data()
# print(table_data)
