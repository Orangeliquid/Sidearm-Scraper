import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# test sheet
# sheet_id = "1rZgzjZa8G-pxWxUgcujP2OSAjz_D4HJRIarrflrOWrk"

# per sheet
sheet_id = "1FYKDzagoEccyLB5vf-7-OUAhNwvpIShnWAOE7fyRN48"
sheet = client.open_by_key(sheet_id)


def find_last_row(sheet_name):
    """
    Finds the last row with data in a given sheet.
    """
    values = sheet_name.get_all_values()
    return len(values)


def post_headers(sheet_name, team_tuple: tuple, start: tuple):
    headers = ["Player", "MP", "PTS", "AST", "OREB", "REB", "FGM", "FGA", "FG%", "FTM", "FTA",
               "FT%", "BLK", "STL", "TOV", "FOUL", "3P", "uPER", "Per"]

    service = build("sheets", "v4", credentials=creds)

    # home_tuple = ("Home", home) - starting = (0, 2)

    # Determine the starting row and column
    start_row = start[0] + 1  # Convert to 1-based index
    start_column = start[1] + 1  # Convert to 1-based index

    # Post team_tuple (e.g., "Home" and team name)
    team_cell_range = f"A{start_row}:B{start_row}"
    sheet_name.update(team_cell_range, [list(team_tuple)], value_input_option="USER_ENTERED")

    # Post headers below the team_tuple
    headers_start_row = start_row + 1
    headers_range = f"A{headers_start_row}:{chr(64 + len(headers))}{headers_start_row}"
    sheet_name.update(headers_range, [headers], value_input_option="USER_ENTERED")

    # Format the headers row to bold
    requests = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_name.id,  # Sheet ID
                        "startRowIndex": start[0],  # Header row (0-based index)
                        "endRowIndex": start[1],  # Up to the next row
                        "startColumnIndex": 0,  # Start column (A)
                        "endColumnIndex": len(headers),  # End column based on number of headers
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat.textFormat.bold",
                }
            }
        ]
    }

    # Execute the batchUpdate request
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_name.spreadsheet.id,
        body=requests
    ).execute()

    print("Headers for both teams appended and formatted to bold!")


def post_player_data(player_data: list, sheet_name: str):
    for player in player_data:
        data = []
        for var, val in player.__dict__.items():
            print(f"{var}: {val}")
            # Skip boolean values
            if isinstance(val, bool):
                continue
            data.append(val)

        # Adjust the range slicing logic as needed
        sheet_name.append_row(data[1:-4], value_input_option="USER_ENTERED")

    print("Player data has been added to the sheet!")


def post_team_totals(sheet_name, starting_cell, last_cell, is_home_team: bool):
    team_totals = ["Team"]
    columns = "BCDEFGHIJKLMNOPQ"
    if is_home_team:
        """
        Post team totals:
        - A12 = Team
        - B-Q12 -> sum of rows 2-11
        - I12 = $G12/$H12
        - L12 = $J12/$H12
        """
        # Team totals row

        data_range = (3, last_cell)  # Rows 3 to last cell
    else:
        data_range = (starting_cell, last_cell)

    # Build formulas for each column
    for column in columns:
        team_totals.append(f"=SUM({column}{data_range[0]}:{column}{data_range[1]})")

    # Append the row using append_row method
    sheet_name.append_row(team_totals, value_input_option="USER_ENTERED")

    # Update formulas for I and L
    cells_to_update = {
        f"I{last_cell + 1}": [[f"=G{last_cell + 1}/H{last_cell + 1}"]],
        f"L{last_cell + 1}": [[f"=J{last_cell + 1}/K{last_cell + 1}"]],
    }

    for cell, formula in cells_to_update.items():
        sheet_name.update(cell, formula, value_input_option="USER_ENTERED")

    # Use Google Sheets API to format the row to bold and percentage
    service = build("sheets", "v4", credentials=creds)
    requests = {
        "requests": [
            # Format the team totals row (Row 12)
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_name.id,
                        "startRowIndex": last_cell,  # Row 12 in zero-index
                        "endRowIndex": last_cell + 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": len(columns) + 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True},
                        }
                    },
                    "fields": "userEnteredFormat.textFormat.bold",
                }
            },
            # Format specific cells FTP and FGP as percentage
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_name.id,
                        "startRowIndex": last_cell,  # Row 12 in zero-index
                        "endRowIndex": last_cell + 1,
                        "startColumnIndex": 8,  # Column I
                        "endColumnIndex": 9,   # Column I (just one column)
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                                "type": "PERCENT",
                                "pattern": "0.00%"  # Format as percentage with 2 decimal places
                            }
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat",
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_name.id,
                        "startRowIndex": last_cell,  # Row 12 in zero-index
                        "endRowIndex": last_cell + 1,
                        "startColumnIndex": 11,  # Column L
                        "endColumnIndex": 12,   # Column L (just one column)
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                                "type": "PERCENT",
                                "pattern": "0.00%"  # Format as percentage with 2 decimal places
                            }
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        ]
    }

    # Execute the batchUpdate request
    service.spreadsheets().batchUpdate(spreadsheetId=sheet_name.spreadsheet.id, body=requests).execute()

    print("Team totals have been added and formatted!")


def post_season_stats(home_data: list, away_data: list, title: str, home: str, away: str):
    """
    Create a new sheet, post team totals, and format cells.
    """
    # Create a new sheet
    new_sheet_name = title
    print(f"Creating new sheet: {new_sheet_name}")
    rows, cols = 50, 25  # Define dimensions for the new sheet (adjust as needed)
    new_sheet = sheet.add_worksheet(title=new_sheet_name, rows=str(rows), cols=str(cols))

    # Post headers and team totals to the new sheet
    home_tuple = ("Home", home)
    starting = (0, 2)

    # Call the correct functions using the `new_sheet` object
    post_headers(new_sheet, home_tuple, starting)
    post_player_data(home_data, new_sheet)

    # Find the last row in the `new_sheet` object - this is the last player in the home team
    last_row_home = find_last_row(new_sheet)

    # post team totals and format with bold
    post_team_totals(sheet_name=new_sheet, starting_cell=3, last_cell=last_row_home, is_home_team=True)

    # find new last row - will be one digit higher than the last_row_home
    home_total_index = find_last_row(new_sheet)

    away_tuple = ("Away", away)
    starting = (home_total_index + 2, home_total_index + 4)

    # Call the correct functions using the `new_sheet` object
    post_headers(new_sheet, away_tuple, starting)
    post_player_data(away_data, new_sheet)

    # Find the last row in the `new_sheet` object - this is the last player in the away team
    last_row_away = find_last_row(new_sheet)

    # post team totals and format with bold
    post_team_totals(sheet_name=new_sheet, starting_cell=starting[1] + 1, last_cell=last_row_away, is_home_team=False)

    # Issues - Away team totals are going from b3 - end of away - need to determine start for away team totalling


if __name__ == '__main__':
    from game_by_game_scraper import fetch_tables, determine_home_away, clean_title, determine_conference
    from sidearm_scraper import Sidearm_Scraper
    from model.player import Player
    from util.per_util import calculate_pers
