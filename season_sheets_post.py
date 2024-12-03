import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import datetime

# Posts current team stats to Google Sheets

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# test sheet
# sheet_id = "1rZgzjZa8G-pxWxUgcujP2OSAjz_D4HJRIarrflrOWrk"

# per sheet
sheet_id = "1FYKDzagoEccyLB5vf-7-OUAhNwvpIShnWAOE7fyRN48"
sheet = client.open_by_key(sheet_id)


def post_headers(sheet_name):
    headers = ["Player", "MP", "PTS", "AST", "OREB", "REB", "FGM", "FGA", "FG%", "FTM", "FTA",
               "FT%", "BLK", "STL", "TOV", "FOUL", "3P", "uPER", "Per"]
    sheet_name.append_row(headers, value_input_option="USER_ENTERED")

    # Use Google Sheets API to format the headers row to bold
    service = build("sheets", "v4", credentials=creds)

    # Format the first row to bold
    requests = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_name.id,  # Use the new sheet's ID
                        "startRowIndex": 0,  # Header row (0-based index)
                        "endRowIndex": 1,   # Up to the next row
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
    service.spreadsheets().batchUpdate(spreadsheetId=sheet_name.spreadsheet.id, body=requests).execute()
    print("Headers appended and formatted to bold!")


def post_player_data(player_data: list, sheet_name):
    for player in player_data:
        data = []
        for var, val in player.__dict__.items():
            if var != "HAS_PLAYED":
                data.append(val)
        sheet_name.append_row(data[2:-1], value_input_option="USER_ENTERED")
    print(f"Player data has been added to the sheet!")


def post_team_totals(sheet_name):
    """
    Post team totals:
    - A12 = Team
    - B-Q12 -> sum of rows 2-11
    - I12 = $G12/$H12
    - L12 = $J12/$H12
    """
    # Team totals row
    team_totals = ["Team"]
    data_range = (2, 11)  # Rows 2 to 11 for summing
    columns = "BCDEFGHIJKLMNOPQ"

    # Build formulas for each column
    for column in columns:
        team_totals.append(f"=SUM({column}{data_range[0]}:{column}{data_range[1]})")

    # Append the row using append_row method
    sheet_name.append_row(team_totals, value_input_option="USER_ENTERED")

    # Update formulas for I12 and L12
    cells_to_update = {
        "I12": [["=G12/H12"]],
        "L12": [["=J12/K12"]],
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
                        "startRowIndex": 11,  # Row 12 in zero-index
                        "endRowIndex": 12,
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
            # Format specific cells (I12 and L12) as percentage
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_name.id,
                        "startRowIndex": 11,  # Row 12 in zero-index
                        "endRowIndex": 12,
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
                        "startRowIndex": 11,  # Row 12 in zero-index
                        "endRowIndex": 12,
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


def post_season_stats(player_data: list):
    """
    Create a new sheet, post team totals, and format cells.
    """
    date = datetime.date.today()
    # Create a new sheet
    new_sheet_name = f"ODU Season Stats({date})"
    print(new_sheet_name)
    rows, cols = 50, 25  # Define dimensions for the new sheet (adjust as needed)
    new_sheet = sheet.add_worksheet(title=new_sheet_name, rows=str(rows), cols=str(cols))

    # Post headers and team totals to the new sheet
    post_headers(new_sheet)
    post_player_data(player_data, new_sheet)
    post_team_totals(new_sheet)
