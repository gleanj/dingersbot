# data_handler.py
# Module for reading the Excel file and normalizing the player roster.

import pandas as pd
import statsapi
import re
import os
import mlb_monitor

# Define the filename for the roster
ROSTER_FILENAME = "dingers.xlsx"

def load_and_normalize_roster():
    """
    Loads the player roster from the Excel file, normalizes player names to player IDs,
    and returns a dictionary optimized for quick lookups.

    The structure of the returned dictionary is:
    {
        'player_id_1': {'name': 'Player Name 1', 'fantasy_team': 'Fantasy Team A'},
        'player_id_2': {'name': 'Player Name 2', 'fantasy_team': 'Fantasy Team B'},
        ...
    }
    This allows for O(1) lookup time when checking if a home run was hit by a tracked player.
    """
    print("Loading and normalizing player roster...")
    
    # Check if the roster file exists in the current directory
    if not os.path.exists(ROSTER_FILENAME):
        print(f"--- ERROR: Roster file '{ROSTER_FILENAME}' not found. ---")
        print("Please make sure the Excel file is in the same directory as the script.")
        return None

    try:
        # Read the Excel file into a pandas DataFrame
        # The first row of the Excel sheet is expected to be the fantasy team names
        df = pd.read_excel(ROSTER_FILENAME)
    except Exception as e:
        print(f"--- ERROR: Could not read the Excel file. ---")
        print(f"Pandas error: {e}")
        return None

    normalized_roster = {}
    
    # Iterate over each column in the DataFrame. Each column header is a fantasy team name.
    for fantasy_team in df.columns:
        print(f"\nProcessing team: {fantasy_team}")
        
        # Iterate over each player in the current column (fantasy team)
        for player_name_raw in df[fantasy_team]:
            # Skip empty cells in the spreadsheet
            if pd.isna(player_name_raw):
                continue

            try:
                # Clean the player name. Example: "Aaron Judge (NYY)" -> "Aaron Judge"
                # This regex removes parentheses and any text inside them, then strips whitespace.
                player_name_cleaned = re.sub(r'\s*\([^)]*\)', '', player_name_raw).strip()

                if not player_name_cleaned:
                    continue

                # Use the MLB-StatsAPI to look up the player by their cleaned name
                player_search_results = statsapi.lookup_player(player_name_cleaned)

                if not player_search_results:
                    print(f"  - WARNING: Could not find player '{player_name_cleaned}'. Skipping.")
                    continue

                # Assume the first result is the correct one.
                # The API returns a list of dictionaries, one for each matching player.
                player_data = player_search_results[0]
                player_id = player_data['id']
                player_full_name = player_data['fullName']

                # Add the player to our normalized roster dictionary
                normalized_roster[player_id] = {
                    'name': player_full_name,
                    'fantasy_team': fantasy_team
                }
                
                bomb_count = mlb_monitor.get_stats_since_break(player_id)

                print(f"  + Found and mapped '{player_full_name}' (ID: {player_id}) - (bombs since break: {bomb_count}))")

            except Exception as e:
                print(f"  - ERROR: An unexpected error occurred while processing '{player_name_raw}'.")
                print(f"    Details: {e}")

    print("\n--- Roster normalization complete! ---")
    print(f"Successfully mapped {len(normalized_roster)} players.")
    return normalized_roster

# This block allows you to test this file directly to see if it works
if __name__ == '__main__':
    print("Running data_handler.py as a standalone script for testing...")
    roster = load_and_normalize_roster()
    
    if roster:
        print("\n--- First 5 players from the normalized roster: ---")
        for i, (player_id, data) in enumerate(roster.items()):
            if i >= 5:
                break
            print(f"ID: {player_id}, Info: {data}")
