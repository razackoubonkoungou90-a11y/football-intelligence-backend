"""
Combine les matchs réels (API-Football) avec les cotes réelles agrégées (The Odds API)
pour proposer une sélection dont la cote totale s'approche de l'intervalle demandé.

IMPORTANT (à garder en tête, voir README) :
- Les cotes viennent de bookmakers "mainstream" (Pinnacle, Bet365, etc. selon la région),
  PAS de Megapari / 1xBet / 1win qui n'ont pas d'API publique. Ce sont donc des cotes
  de référence, pas une garantie de ce que l'utilisateur verra sur son bookmaker.
- Plus la cote totale cible est haute (accumulateur de nombreux matchs), plus la probabilité
  réelle que TOUS les matchs passent devient faible — ce service ne "fabrique" aucune chance
  supplémentaire, il ne fait qu'assembler des données réelles.
"""
import random
from app.clients import api_football, odds_api
from app.models.schemas import CouponRequest, CouponResponse, MatchSelection

WARNING_TEXT = (
    "Cotes de référence issues de bookmakers agrégés (pas Megapari/1xBet/1win). "
    "Aucune garantie que le résultat corresponde à un vrai coupon jouable tel quel."
)


def _match_fixture_to_odds(fixture: dict, odds_events: list[dict]) -> dict | None:
    """Associe un fixture API-Football à un événement The Odds API par noms d'équipes."""
    for event in odds_events:
        if event.get("home_team") == fixture["home"] and event.get("away_team") == fixture["away"]:
            return event
    return None


async def generate_coupon(req: CouponRequest) -> CouponResponse:
    fixtures_raw = await api_football.get_fixtures(date=req.date)
    fixtures = [api_football.normalize_fixture(f) for f in fixtures_raw]

    sport_key = odds_api.SPORT_KEYS.get(req.sports[0] if req.sports else "football", "soccer_epl")
    odds_events = await odds_api.get_odds(sport_key=sport_key)

    candidates: list[MatchSelection] = []
    for fx in fixtures:
        event = _match_fixture_to_odds(fx, odds_events)
        if not event:
            continue
        odd = odds_api.best_average_odd(event, fx["home"])
        if odd:
            candidates.append(MatchSelection(
                fixture_id=fx["id"], competition=fx["competition"],
                home=fx["home"], away=fx["away"],
                market="1N2 : victoire domicile", odd=odd,
                sources=len(event.get("bookmakers", [])),
            ))

    random.shuffle(candidates)
    selections: list[MatchSelection] = []
    total = 1.0
    for c in candidates:
        if len(selections) >= req.max_matches:
            break
        if total * c.odd > req.odd_max * 1.3:
            continue
        selections.append(c)
        total *= c.odd
        if req.odd_min <= total <= req.odd_max:
            break

    return CouponResponse(selections=selections, total_odd=round(total, 2), warning=WARNING_TEXT)
