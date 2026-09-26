"""
Client pour API-Football (api-sports.io).
Récupère les matchs (fixtures) réels par date / ligue.
Doc : https://www.api-football.com/documentation-v3
"""
import httpx
from app.config import API_FOOTBALL_BASE_URL, API_FOOTBALL_HOST, API_FOOTBALL_KEY

HEADERS = {
    "x-rapidapi-key": API_FOOTBALL_KEY,
    "x-rapidapi-host": API_FOOTBALL_HOST,
}


async def get_fixtures(date: str, league: int | None = None, season: int | None = None) -> list[dict]:
    """
    date : format 'YYYY-MM-DD'
    league : id de compétition API-Football (optionnel, sinon toutes les ligues couvertes par le plan)
    Retourne une liste de matchs bruts (dict API-Football).
    """
    params = {"date": date}
    if league:
        params["league"] = league
    if season:
        params["season"] = season

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{API_FOOTBALL_BASE_URL}/fixtures", headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", [])


def normalize_fixture(raw: dict) -> dict:
    """Transforme une réponse API-Football brute en format interne simple."""
    fixture = raw.get("fixture", {})
    league = raw.get("league", {})
    teams = raw.get("teams", {})
    return {
        "id": fixture.get("id"),
        "date": fixture.get("date"),
        "status": fixture.get("status", {}).get("short"),
        "competition": league.get("name"),
        "league_id": league.get("id"),
        "season": league.get("season"),
        "country": league.get("country"),
        "home": teams.get("home", {}).get("name"),
        "home_id": teams.get("home", {}).get("id"),
        "away": teams.get("away", {}).get("name"),
        "away_id": teams.get("away", {}).get("id"),
    }


async def get_team_statistics(team_id: int, league_id: int, season: int) -> dict:
    """
    Stats moyennes d'une équipe sur une saison (buts marqués/encaissés, domicile/extérieur).
    Doc : https://www.api-football.com/documentation-v3#operation/get-teams-statistics
    """
    params = {"team": team_id, "league": league_id, "season": season}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{API_FOOTBALL_BASE_URL}/teams/statistics", headers=HEADERS, params=params)
        resp.raise_for_status()
        return resp.json().get("response", {})


def extract_goal_averages(stats: dict) -> dict:
    """Simplifie la réponse /teams/statistics en moyennes de buts marqués/encaissés (domicile/extérieur)."""
    goals = stats.get("goals", {})
    def avg(side_dict, side):
        try:
            return float(side_dict.get("average", {}).get(side, 0) or 0)
        except (TypeError, ValueError):
            return 0.0
    return {
        "scored_home": avg(goals.get("for", {}), "home"),
        "scored_away": avg(goals.get("for", {}), "away"),
        "conceded_home": avg(goals.get("against", {}), "home"),
        "conceded_away": avg(goals.get("against", {}), "away"),
  }
