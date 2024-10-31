import json


# Cleans the team category further by eliminating unnecessary titles and extra layers of JSON
def clean_team_data(file):
    with open(file, 'r') as f:
        data = json.load(f)

    # retrieve top key for JSON (assume it's the first key)
    top = list(data.keys())[0]

    # parse JSON to find team level and target level
    team_level = data.get(top, {}).get('Team', {})
    if not team_level:
        raise ValueError("Team data not found")

    target_level = list(team_level.keys())[0]
    team_data = team_level.get(target_level, [])

    # Initialize variables to hold the organized structure
    organized_data = {}
    current_category = None

    # Iterate over the list (assuming team_data is a list of dictionaries)
    for entry in team_data:
        if isinstance(entry, dict):
            entry_keys = list(entry.keys())
            if len(entry_keys) < 2:
                print(f"Skipping malformed entry: {entry}")
                continue

            stat_key, team_key = entry_keys[0], entry_keys[1]

            # Check if the entry is a category (where stat_key matches team_key value)
            if entry[stat_key] == entry[team_key]:
                # This is a new category, create a new entry in the organized_data
                current_category = entry[stat_key]  # Example: "Scoring", "Shooting"
                organized_data[current_category] = {}
            else:
                # Add this entry directly under the current category
                if current_category:
                    organized_data[current_category][entry[stat_key]] = {
                        team_key: entry[team_key],
                        "Opponents": entry.get("Opponents  OPP", "N/A")  # Add fallback for missing opponent data
                    }

    # Replace the old team data with the new structure
    data[top]['Team'][target_level] = organized_data
    new_file_name = f"{file.split('.')[0]}_Modified.json"

    with open(new_file_name, 'w') as f:
        json.dump(data, f, indent=4)

    # Print the new structure to verify
    # print(json.dumps(organized_data, indent=4))

    return new_file_name


# file_to_pass = "Walsh_Tables_Data_2023-24.json"
# test = clean_team_data(file_to_pass)
# -------------------------------------------------------------------------------------------------------------------
# Aims to clean the 'Individual" category data
def clean_individual_data(file: str):
    with open(file, 'r') as f:
        data = json.load(f)

    # Extract top key of data
    top = list(data.keys())[0]

    individual_level = data.get(top, {}).get('Individual', {})

    if not individual_level:
        raise ValueError("Individual data not found")

    # Extract subheading names (first two)
    overall_and_conference_targets = list(individual_level.keys())[:2]
    print("Target Levels:", overall_and_conference_targets)

    for target in overall_and_conference_targets:
        target_data = individual_level.get(target, [])
        organized_data = {}

        # Process each player
        for player in target_data:
            name = player.get('Player Player', '')
            name_parts = name.split(" ")

            # Handle cases where the player has a single name or multiple names
            try:
                name = name_parts[0] + " " + name_parts[1]
            except IndexError:
                name = name_parts[0]

            # Organize the player's stats
            organized_data[name] = {
                "#": player.get("# #", ""),
                "GP": player.get('GP GP', ""),
                "GS": player.get("GS GS", ""),
                "Minutes TOT": player.get("Minutes TOT", ""),
                "Minutes AVG": player.get("Minutes AVG", ""),
                "FGM": player.get("FG FGM", ""),
                "FGA": player.get("FG FGA", ""),
                "FG%": player.get("FG FG%", ""),
                "3PT": player.get("3PT 3PT", ""),
                "3PTA": player.get("3PT 3PTA", ""),
                "3PT%": player.get("3PT 3PT%", ""),
                "FTM": player.get("FT FTM", ""),
                "FTA": player.get("FT FTA", ""),
                "FT%": player.get("FT FT%", ""),
                "Scoring PTS": player.get("Scoring PTS", ""),
                "Scoring AVG": player.get("Scoring AVG", ""),
                "Rebounds OFF": player.get("Rebounds OFF", ""),
                "Rebounds DEF": player.get("Rebounds DEF", ""),
                "Rebounds TOT": player.get("Rebounds TOT", ""),
                "Rebounds AVG": player.get("Rebounds AVG", ""),
                "PF": player.get("PF PF", ""),
                "AST": player.get("AST AST", ""),
                "TO": player.get("TO TO", ""),
                "STL": player.get("STL STL", ""),
                "BLK": player.get("BLK BLK", "")
            }
            print(f"Cleaned Data for {name}:")
            print(organized_data[name])

        # Update the original JSON structure with the organized data
        data[top]['Individual'][target] = organized_data

    scoring_and_averages_targets = list(individual_level.keys())[2:]
    print("Target Levels:", scoring_and_averages_targets)

    for target in scoring_and_averages_targets:
        target_data = individual_level.get(target, [])
        organized_data = {}

        # Process each player
        for player in target_data:
            name = player.get('Player Player', '')
            name_parts = name.split(" ")
            refined_dict = {}
            # Handle cases where the player has a single name or multiple names
            try:
                name = name_parts[0] + " " + name_parts[1]
            except IndexError:
                name = name_parts[0]

            key_list = list(player.keys())
            for key in key_list:
                new_name = key.split()[-1]
                refined_dict[new_name] = player[key]

            # remove 'Player' value as this is the new data header
            del refined_dict['Player']
            organized_data[name] = refined_dict

        # # Update the original JSON structure with the organized data
        data[top]['Individual'][target] = organized_data

    # # Save the updated data back to a new JSON file
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

    # # # Print the new structure to verify
    # print(json.dumps(data[top]['Individual'], indent=4))


# file_to_clean = "Ohio_Dominican_University_Tables_Data_2023-24_Modified.json"
# clean_individual_data(file_to_clean)

# -------------------------------------------------------------------------------------------------------------------
# Aims to clean 'GAME-BY-GAME' category data
def clean_game_by_game_data(file: str):
    with open(file, 'r') as f:
        data = json.load(f)

    # Extract top key of data
    top = list(data.keys())[0]

    # access Game-By-Game level in json
    game_by_game_level = data.get(top, {}).get('Game-By-Game', {})

    if not game_by_game_level:
        raise ValueError("Game-By-Game data not found")

    game_by_game_keys = list(game_by_game_level.keys())

    # loop through all the keys in Game-By-Game category
    for target in game_by_game_keys:
        # store new data with opponent name as key
        organized_data = {}
        # parse only iterated key data
        target_data = game_by_game_level.get(target, [])
        # loop through entry data in specific target
        for entry in target_data:
            # define Opponent value as new key to be set
            name = entry.get("Opponent")
            refined_dict = {}
            key_list = list(entry.keys())
            # iterate through key list of each entry
            for key in key_list:
                # add value as is to refined dict
                refined_dict[key] = entry[key]

            # remove Opponent key value pair seeing as value is used as the new key for this section
            del refined_dict['Opponent']
            organized_data[name] = refined_dict

        # Update the original JSON structure with the organized data
        data[top]['Game-By-Game'][target] = organized_data

    # Save the updated data back to a new JSON file
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)
    # # Print the new structure to verify
    # print(json.dumps(data[top]['Game-By-Game'], indent=4))


# file_to_clean = "Ohio_Dominican_University_Tables_Data_2023-24_Modified.json"
# clean_game_by_game_data(file_to_clean)

# -------------------------------------------------------------------------------------------------------------------
# Aims to clean Game Highs category data
def clean_game_highs_data(file: str):
    with open(file, 'r') as f:
        data = json.load(f)

    # Extract top key of data
    top = list(data.keys())[0]

    # access Game Highs level in json
    game_highs_level = data.get(top, {}).get('Game Highs', {})

    if not game_highs_level:
        raise ValueError("Game Highs data not found")

    # create list of Game Highs keys
    game_highs_keys = list(game_highs_level.keys())

    # loop through each target in game_high_keys
    for target in game_highs_keys:
        organized_data = {}
        target_data = game_highs_level.get(target, [])
        # loop through each entry of target_data
        for entry in target_data:
            name = entry.get('Statistic')
            refined_dict = {}
            keys_list = list(entry.keys())
            # loop through all key value pairs in entry
            for key in keys_list:
                refined_dict[key] = entry[key]

            # delete Statistic as this value is the new name for the entry
            del refined_dict['Statistic']
            organized_data[name] = refined_dict

        # Change sub category names to be similar
        if target == "Team_2":
            data[top]['Game Highs']["Team Highs"] = organized_data
            del data[top]['Game Highs'][target]
        elif target == "Individual":
            data[top]['Game Highs']["Individual Highs"] = organized_data
            del data[top]['Game Highs'][target]
        else:
            data[top]['Game Highs'][target] = organized_data

    # Save the updated data back to a new JSON file
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)
    # Print the new structure to verify
    # print(json.dumps(data[top]['Game Highs'], indent=4))


# file_to_clean = "Ohio_Dominican_University_Tables_Data_2023-24_Modified.json"
# clean_game_highs_data(file_to_clean)

# -------------------------------------------------------------------------------------------------------------------
# Aims to clean Category Leaders category data
def clean_category_leaders_data(file: str):
    with open(file, 'r') as f:
        data = json.load(f)

    # Extract top key of data
    top = list(data.keys())[0]

    # access Game Highs level in json
    category_leaders_level = data.get(top, {}).get('Category Leaders', {})

    if not category_leaders_level:
        raise ValueError("Category Leaders data not found")

    # create list of Category Leaders keys
    category_leaders_keys = list(category_leaders_level.keys())

    # loop through each target in category_leaders_keys
    for target in category_leaders_keys:
        organized_data = {}
        target_data = category_leaders_level.get(target, [])
        # loop through each entry of target_data
        for entry in target_data:
            # remove number in name and put last name and first together to keep consistent from other categories
            name = " ".join(entry.get('Name').split()[1:3])
            refined_dict = {}
            keys_list = list(entry.keys())
            # loop through all key value pairs in entry
            for key in keys_list:
                refined_dict[key] = entry[key]

            # delete Name as this value is the new name for the entry
            del refined_dict['Name']
            organized_data[name] = refined_dict

        data[top]['Category Leaders'][target] = organized_data

    # Save the updated data back to a new JSON file
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)
    # Print the new structure to verify
    # print(json.dumps(data[top]['Category Leaders'], indent=4))


# file_to_clean = "Ohio_Dominican_University_Tables_Data_2023-24_Modified.json"
# clean_category_leaders_data(file_to_clean)

# -------------------------------------------------------------------------------------------------------------------
