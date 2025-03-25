import requests
import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.core.credentials import AzureKeyCredential

load_dotenv()

class GameDayNotification:
    def __init__(self):
        self.api_key = os.getenv("SPORTS_API_KEY")
        self.topic_endpoint = os.getenv("EVENT_GRID_TOPIC_ENDPOINT")
        self.topic_key = os.getenv("EVENT_GRID_TOPIC_KEY")
        logging.info("GameDayNotifications initialized.")

    def fetch_sports_data(self):
        """Fetch data from the API URL."""

        utc_now = datetime.now(timezone.utc)
        central_time = utc_now - timedelta(hours=6)
        today_date = central_time.strftime("%Y-%m-%d")
        api_url = f"https://api.sportsdata.io/v3/nba/scores/json/GamesByDate/{today_date}?key={self.api_key}"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching data from API: {e}")
            return None

    def format_game_data(self, game):
        """Format the game data for display."""

        status = game.get("Status", "Unknown")
        away_team = game.get("AwayTeam", "Unknown")
        home_team = game.get("HomeTeam", "Unknown")
        final_score = (
            f"{game.get('AwayTeamScore', 'N/A')}-{game.get('HomeTeamScore', 'N/A')}"
        )
        start_time = game.get("DateTime", "Unknown")
        channel = game.get("Channel", "Unknown")

        # Format quarters
        quarters = game.get("Quarters", [])
        quarter_scores = ", ".join(
            [
                f"Q{q['Number']}: {q.get('AwayScore', 'N/A')}-{q.get('HomeScore', 'N/A')}"
                for q in quarters
            ]
        )

        if status == "Final":
            return (
                f"Game Status: {status}<br>"
                f"{away_team} vs {home_team}<br>"
                f"Final Score: {final_score}<br>"
                f"Start Time: {start_time}<br>"
                f"Channel: {channel}<br>"
                f"Quarter Scores: {quarter_scores}<br>"
            )
        elif status == "InProgress":
            last_play = game.get("LastPlay", "N/A")
            return (
                f"Game Status: {status}<br>"
                f"{away_team} vs {home_team}<br>"
                f"Current Score: {final_score}<br>"
                f"Last Play: {last_play}<br>"
                f"Channel: {channel}<br>"
            )
        elif status == "Scheduled":
            return (
                f"Game Status: {status}<br>"
                f"{away_team} vs {home_team}<br>"
                f"Start Time: {start_time}<br>"
                f"Channel: {channel}<br>"
            )
        else:
            return (
                f"Game Status: {status}<br>"
                f"{away_team} vs {home_team}<br>"
                f"Details are unavailable at the moment.<br>"
            )

    def publish_to_topic(self, sports_data):
        """Publish the game data to an Azure Event Grid topic."""
        if not sports_data:
            logging.info("No sports data available for publishing.")
            return

        messages = [self.format_game_data(game) for game in sports_data]
        final_message = "<br>---<br>".join(messages) if messages else "No games available for today."
        try:
            event_client = EventGridPublisherClient(
                self.topic_endpoint, AzureKeyCredential(self.topic_key)
            )

            event = EventGridEvent(
                subject="GameDayNotifications",
                data=final_message,
                event_type="GameDayNotification",
                data_version="1.0",
            )
            print('-------------------------------')
            print(event)
            event_client.send([event])
            logging.info("Event published to Event Grid topic.")
            print("Event published to Event Grid topic.")
        except Exception as e:
            logging.error(f"Error publishing event to Event Grid: {e}")
            print(f"Error publishing event to Event Grid: {e}")
            return


if __name__ == "__main__":
    game_day_notification = GameDayNotification()