# twitter_client.py
# Module for all interactions with the Tweepy/Twitter API.

import tweepy
import config  # Imports your credentials from config.py

def create_client():
    """
    Creates and returns an authenticated Tweepy Client for Twitter API v2.
    
    This function reads the credentials from the config.py file and uses
    them to authenticate. It's best practice to have this logic separate
    so that authentication is handled cleanly in one place.
    
    Returns:
        An authenticated tweepy.Client object, or None if authentication fails.
    """
    try:
        client = tweepy.Client(
            consumer_key=config.TWITTER_API_KEY,
            consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET
        )
        print("Successfully created Twitter API client.")
        return client
    except Exception as e:
        print("--- CRITICAL ERROR: Failed to create Twitter API client. ---")
        print(f"    Error: {e}")
        print("    Please check that your credentials in config.py are correct.")
        return None

def post_homerun_tweet(client, player_name, fantasy_team, new_score, description):
    """
    Crafts and posts a tweet announcing a home run.

    Args:
        client (tweepy.Client): The authenticated Tweepy client object.
        player_name (str): The name of the player who hit the home run.
        fantasy_team (str): The fantasy team the player belongs to.
        new_score (int): The new total score for the fantasy team.
        description (str): The play-by-play description of the home run.
    
    Returns:
        True if the tweet was posted successfully, False otherwise.
    """
    # --- Craft the tweet text ---
    # Example:
    # 🚨 DINGER ALERT! 🚨
    # Aaron Judge hits a home run! (450 ft, 2 RBI)
    #
    # That's homer #11 for fantasy team "Iron Man"!
    # #FantasyBaseball #Homerun #MLB
    
    # Extract details from the description if possible, e.g., distance or RBIs
    # This is a simple example; more complex parsing could be added.
    play_details = f"({description.split(',')[1].strip()})" if ',' in description else ""

    tweet_text = (
        f"🚨 DINGER ALERT! 🚨\n\n"
        f"{player_name} just went deep! {play_details}\n\n"
        f"That's homer #{new_score} for team \"{fantasy_team}\"!\n"
        
    )

    # Ensure the tweet does not exceed the 280 character limit
    if len(tweet_text) > 280:
        # If it's too long, create a simpler version
        tweet_text = (
            f"🚨 DINGER! 🚨 {player_name} of \"{fantasy_team}\" just crushed one!\n"
            f"That's team homer #{new_score}!\n"

        )

    print("\n--- Attempting to post tweet ---")
    print(f"Content:\n{tweet_text}")

    try:
        # Use the client to post the tweet
        client.create_tweet(text=tweet_text)
        print("--- Tweet posted successfully! ---")
        return True
    except tweepy.errors.TweepyException as e:
        print("--- ERROR: Failed to post tweet. ---")
        print(f"    Tweepy Error: {e}")
        return False
    except Exception as e:
        print("--- ERROR: An unexpected error occurred while posting the tweet. ---")
        print(f"    Error: {e}")
        return False

# This module is not designed to be run directly, as it requires a live event.
# Its functions will be called by main.py when a home run is detected.
if __name__ == '__main__':
    print("--- Twitter Client Module ---")
    print("This module is intended to be imported by main.py.")
    print("It handles creating the Twitter client and posting tweets.")
