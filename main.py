# main.py
# The central orchestrator for the MLB Homerun Bot.

import time
import logging
from datetime import datetime

# Import all the custom modules we've built
import data_handler
import mlb_monitor
import state_manager
import twitter_client

# --- Configuration ---
GAME_CHECK_INTERVAL = 300  # 5 minutes
PLAY_CHECK_INTERVAL = 30

def setup_logging():
    """Configures the logging for the application."""
    # FIX: Add encoding='utf-8' to the FileHandler to support unicode characters like emojis.
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("bot.log", encoding='utf-8'),
                            logging.StreamHandler()
                        ])

def run_bot():
    """
    The main execution function for the Homerun Bot.
    """
    setup_logging()
    logging.info("--- ⚾ MLB Homerun Bot Starting Up... ---")

    # --- Step 1: Initialization ---
    logging.info("[1/5] Loading and normalizing player roster...")
    tracked_players = data_handler.load_and_normalize_roster()
    if not tracked_players:
        logging.critical("Could not load roster. Bot cannot start.")
        return

    logging.info("[2/5] Loading scoreboard...")
    scoreboard = state_manager.load_scoreboard(tracked_players)

    logging.info("[3/5] Loading seen plays history...")
    # This set will now be persistent across restarts
    seen_plays = state_manager.load_seen_plays()

    logging.info("[4/5] Authenticating with Twitter...")
    x_client = twitter_client.create_client()
    if not x_client:
        logging.critical("Could not create Twitter client. Bot cannot start.")
        return

    logging.info("[5/5] Initializing runtime variables...")
    active_game_pks = []
    last_game_check_time = 0
    
    logging.info("--- ✅ Initialization Complete. Entering Main Monitoring Loop. ---")
    logging.info("Press Ctrl+C to stop the bot at any time.")

    # --- Step 2: Main Loop ---
    try:
        while True:
            current_time = time.time()

            if current_time - last_game_check_time > GAME_CHECK_INTERVAL:
                logging.info("Checking for active games...")
                active_game_pks = mlb_monitor.get_active_game_pks()
                if active_game_pks:
                    logging.info(f"Found {len(active_game_pks)} live game(s). Now monitoring.")
                else:
                    logging.info("No live games found. Will check again later.")
                last_game_check_time = current_time

            if not active_game_pks:
                time.sleep(PLAY_CHECK_INTERVAL)
                continue

            for game_pk in active_game_pks:
                # Pass the persistent seen_plays set to the monitor
                homerun_event = mlb_monitor.check_for_homeruns(game_pk, tracked_players, seen_plays)

                if homerun_event:
                    # The check_for_homeruns function adds the play to the set.
                    # We now save the updated set to disk immediately to ensure persistence.
                    state_manager.save_seen_plays(seen_plays)
                    
                    fantasy_team = homerun_event['fantasy_team']
                    
                    # 1. Update the score
                    scoreboard[fantasy_team] += 1
                    new_score = scoreboard[fantasy_team]
                    logging.info(f"Score updated for '{fantasy_team}'. New score: {new_score}")
                    
                    # 2. Save the new score to the file
                    state_manager.save_scoreboard(scoreboard)
                    
                    # 3. Post the tweet
                    twitter_client.post_homerun_tweet(
                        client=x_client,
                        player_name=homerun_event['name'],
                        fantasy_team=fantasy_team,
                        new_score=new_score,
                        description=homerun_event['description']
                    )

            time.sleep(PLAY_CHECK_INTERVAL)

    except KeyboardInterrupt:
        logging.info("--- Bot shutting down manually. Goodbye! ---")
    except Exception as e:
        logging.critical("--- AN UNEXPECTED ERROR OCCURRED! ---", exc_info=True)
        logging.info("The bot will attempt to restart in 60 seconds...")
        time.sleep(60)
        run_bot()

if __name__ == '__main__':
    run_bot()
