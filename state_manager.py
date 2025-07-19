# state_manager.py
# Module for reading and writing the persistent scoreboard and seen plays.

import json
import os
import logging

# Define the filenames for our persistent data
SCOREBOARD_FILENAME = "scoreboard.json"
SEEN_PLAYS_FILENAME = "seen_plays.json"

def load_scoreboard(tracked_players):
    """
    Loads the scoreboard from scoreboard.json. If the file doesn't exist,
    it initializes a new scoreboard based on the fantasy teams in the roster.
    """
    if os.path.exists(SCOREBOARD_FILENAME):
        logging.info(f"Found existing scoreboard file. Loading '{SCOREBOARD_FILENAME}'...")
        try:
            with open(SCOREBOARD_FILENAME, 'r') as f:
                scoreboard = json.load(f)
            logging.info("Scoreboard loaded successfully.")
            return scoreboard
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Could not read or parse '{SCOREBOARD_FILENAME}': {e}. Starting fresh.")
    
    logging.info("No valid scoreboard found. Initializing a new one...")
    fantasy_teams = set(player['fantasy_team'] for player in tracked_players.values())
    new_scoreboard = {team: 0 for team in fantasy_teams}
    save_scoreboard(new_scoreboard)
    logging.info("New scoreboard created and saved.")
    return new_scoreboard

def save_scoreboard(scoreboard_data):
    """Saves the provided scoreboard dictionary to the scoreboard.json file."""
    try:
        with open(SCOREBOARD_FILENAME, 'w') as f:
            json.dump(scoreboard_data, f, indent=4)
    except IOError as e:
        logging.critical(f"Could not save scoreboard to '{SCOREBOARD_FILENAME}': {e}")

def load_seen_plays():
    """
    Loads the set of seen play IDs from seen_plays.json.
    Returns an empty set if the file doesn't exist or is invalid.
    """
    if os.path.exists(SEEN_PLAYS_FILENAME):
        logging.info(f"Found existing seen plays file. Loading '{SEEN_PLAYS_FILENAME}'...")
        try:
            with open(SEEN_PLAYS_FILENAME, 'r') as f:
                # Load the list from JSON and convert it to a set
                plays_list = json.load(f)
                logging.info(f"Loaded {len(plays_list)} seen play IDs.")
                return set(plays_list)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Could not read or parse '{SEEN_PLAYS_FILENAME}': {e}. Starting with an empty set.")
    
    logging.info("No seen plays file found. Starting with an empty set.")
    return set()

def save_seen_plays(seen_plays_set):
    """Saves the provided set of seen play IDs to the seen_plays.json file."""
    try:
        with open(SEEN_PLAYS_FILENAME, 'w') as f:
            # Convert the set to a list to make it JSON serializable
            json.dump(list(seen_plays_set), f, indent=4)
    except IOError as e:
        logging.error(f"Could not save seen plays to '{SEEN_PLAYS_FILENAME}': {e}")
