"""
Client pour The Odds API (the-odds-api.com).
Récupère des cotes RÉELLES agrégées de bookmakers courants (PAS Megapari / 1xBet / 1win,
qui n'exposent aucune API publique — voir README).
Doc : https://the-odds-api.com/liveapi/guides/v4/
"""
import httpx
from app.config import ODDS_API_BASE_URL, ODDS_API_KEY

# Quelques clés de sport utiles (voir /sports pour la liste complète)
SPORT_KEYS = {
    "football": "soccer_epl",  # à adapter par championnat, ex: soccer_uefa_nations_league
    "basket": "basketball_nba",
    "tennis": "tennis_atp",
    "hockey": "icehockey_nhl",
}


async def list_sports() -> list[dict]:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{ODDS_API_BASE_URL}/sports", params={"apiKey": ODDS_API_KEY})
        resp.raise_for_status()
        return resp.json()


async def get_odds(sport_key: str, regions: str = "eu", markets: str = "h2h") -> list[dict]:
    """
    sport_key : ex 'soccer_epl' (voir list_sports() ou SPORT_KEYS)
    regions : 'eu', 'uk', 'us', 'au' — détermine quels bookmakers sont interrogés
    markets : 'h2h' (1N2), 'totals' (over/under), 'spreads' (handicap)
    """
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": regions,
        "markets": markets,
        "oddsFormat": "decimal",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{ODDS_API_BASE_URL}/sports/{sport_key}/odds", params=params)
        resp.raise_for_status()
        return resp.json()


def best_average_odd(event: dict, outcome_name: str) -> float | None:
    """Fait la moyenne des cotes de tous les bookmakers pour une issue donnée (ex: nom d'une équipe)."""
    values = []
    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            for outcome in market.get("outcomes", []):
