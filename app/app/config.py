import os
from dotenv import load_dotenv

load_dotenv()

API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")
API_FOOTBALL_HOST = os.getenv("API_FOOTBALL_HOST", "v3.football.api-sports.io")
API_FOOTBALL_BASE_URL = f"https://{API_FOOTBALL_HOST}"

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
