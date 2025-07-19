# MLB Homerun Bot

## Overview

This is an automated Python bot that monitors live MLB games in real-time. It's designed to track a specific roster of players from a fantasy baseball league. When a player on the roster hits a home run, the bot automatically posts a notification tweet to a designated X (formerly Twitter) account and updates a persistent scoreboard.

This project was built to run from July 18, 2025, through the end of the MLB regular season.

## Features

- **Real-Time Monitoring:** Polls the MLB Stats API for live game data.
- **Player Tracking:** Reads a player roster from an dingers.xlsx file.
- **Home Run Detection:** Parses play-by-play data to identify home run events for tracked players.
- **Automated Tweeting:** Posts a formatted notification to a Twitter account using the Tweepy library.
- **Persistent Scoring:** Keeps a running total of home runs for each fantasy team in a scoreboard.json file.
- **Resilient:** Designed to handle API inconsistencies and restarts without sending duplicate notifications.

## Setup and Installation

To run this bot, you'll need Python 3 installed.

1.  **Clone the repository:**
    git clone <your-repo-url>
    cd homerun-bot-github

2.  **Create and activate a virtual environment:**
    python -m venv venv
    .\venv\Scripts\activate

3.  **Install the dependencies:**
    pip install -r requirements.txt

4.  **Configure your credentials:**
    - Rename the config.py.example file to config.py.
    - Open config.py and fill in your four X/Twitter API credentials.

5.  **Add your roster:**
    - Place your dingers.xlsx file in the main project directory. The format should have fantasy team names as the column headers and player names in the rows below.

## How to Run the Bot

Once everything is set up, you can start the bot by running the main script from your terminal:

python main.py
