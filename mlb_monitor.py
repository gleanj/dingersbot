# mlb_monitor.py
# Module for all interactions with the MLB-StatsAPI.

import statsapi
import logging
import hashlib
from datetime import datetime
import requests


def get_stats_since_break(person_id, group="hitting"):
    url = f"https://statsapi.mlb.com/api/v1/people/{person_id}/stats"
    params = {
        "stats": "gameLog",
        "group": group,
        "startDate": "2025-07-16"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    bomb_data = response.json()
    bomb_count = 0
    for game in bomb_data['stats'][0]['splits']:
        hr = game['stat'].get('homeRuns', 0)
        bomb_count+= hr
    return bomb_count

def get_player(player_id):

    playerStats = statsapi.player_stat_data(player_id, group="[hitting]", type="season", sportId=1, season=2025)

    return playerStats
    

def get_active_game_pks():
    """
    Queries the MLB API for today's schedule and returns a list of gamePks for
    games that are currently live.
    """
    today_str = datetime.now().strftime('%Y-%m-%d')
    try:
        schedule = statsapi.schedule(date=today_str, sportId=1)
    except Exception as e:
        logging.error(f"Could not fetch schedule from MLB API. Error: {e}")
        return []
    
    active_game_pks = []
    # More robust check for live game statuses
    live_statuses = ['In Progress', 'Live', 'Warmup', 'Pre-Game']
    
    for game in schedule:
        if game.get('status') in live_statuses:
            active_game_pks.append(game['game_id'])
            
    return active_game_pks

def check_for_homeruns(game_pk, tracked_players, seen_plays):
    """
    Checks a specific game for new home run plays by players we are tracking.
    """
    try:
        plays = statsapi.game_scoring_plays(game_pk)
    except Exception as e:
        logging.error(f"Could not fetch scoring plays for game {game_pk}. Error: {e}")
        return None

    # Case 1: The API returns a single string containing one or more plays.
    if isinstance(plays, str):
        individual_play_blocks = plays.strip().split('\n\n')
        
        for play_block in individual_play_blocks:
            main_play_line = play_block.split('\n')[0].strip()

            if not main_play_line:
                continue

            play_hash = hashlib.sha256(main_play_line.encode()).hexdigest()
            play_id = f"{game_pk}-{play_hash}"

            if play_id in seen_plays:
                continue

            if "home run" in main_play_line.lower() or "homers" in main_play_line.lower():
                for player_id, player_data in tracked_players.items():
                    # More robust matching: Check if player's last name is in the description
                    player_last_name = player_data['name'].split(' ')[-1]
                    if player_last_name in main_play_line:
                        seen_plays.add(play_id)
                        player_info = tracked_players[player_id]
                        logging.info(f"!!! DINGER DETECTED (from parsed string) !!!")
                        logging.info(f"  - Player: {player_info['name']}")
                        logging.info(f"  - Fantasy Team: {player_info['fantasy_team']}")
                        return {
                            'name': player_info['name'],
                            'fantasy_team': player_info['fantasy_team'],
                            'description': main_play_line
                        }
        return None

    # Case 2: The API returns a list of play dictionaries (expected behavior).
    elif isinstance(plays, list):
        for play in reversed(plays):
            if not isinstance(play, dict) or not isinstance(play.get('about'), dict) or 'atBatIndex' not in play.get('about', {}):
                continue
                
            play_id = f"{game_pk}-{play['about']['atBatIndex']}"
            
            if play_id in seen_plays:
                continue
                
            seen_plays.add(play_id)

            description = play.get('result', {}).get('description', '')
            if "home run" in description.lower():
                homerun_hitter_id = play['matchup']['batter']['id']
                
                if homerun_hitter_id in tracked_players:
                    player_info = tracked_players[homerun_hitter_id]
                    logging.info(f"!!! DINGER DETECTED (from list format) !!!")
                    logging.info(f"  - Player: {player_info['name']}")
                    logging.info(f"  - Fantasy Team: {player_info['fantasy_team']}")
                    return {
                        'name': player_info['name'],
                        'fantasy_team': player_info['fantasy_team'],
                        'description': description
                    }
        return None

    # Case 3: The API returns something else entirely.
    else:
        logging.warning(f"Received unexpected data format for scoring plays in game {game_pk}. Expected a list or string, but got {type(plays)}. Skipping check.")
        return None
