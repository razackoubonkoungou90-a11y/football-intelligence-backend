from fastapi import FastAPI, HTTPException
from app.clients import api_football
from app.models.schemas import (
    CouponRequest, CouponResponse, MatchPredictionRequest, CouponPredictionRequest,
)
from app.services.coupon_generator import generate_coupon
from app.services import prediction_engine

app = FastAPI(title="Football Intelligence AI — Backend")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/fixtures")
async def fixtures(date: str):
    """Ex: /fixtures?date=2026-09-26"""
    raw = await api_football.get_fixtures(date=date)
    return [api_football.normalize_fixture(f) for f in raw]


@app.post("/coupon", response_model=CouponResponse)
async def coupon(req: CouponRequest):
    try:
        return await generate_coupon(req)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur en récupérant les données : {e}")


@app.post("/predict/match")
async def predict_match(req: MatchPredictionRequest):
    """Probabilités pour un seul match, basées sur les stats réelles de la saison."""
    try:
        home_stats_raw = await api_football.get_team_statistics(req.home_team_id, req.league_id, req.season)
        away_stats_raw = await api_football.get_team_statistics(req.away_team_id, req.league_id, req.season)
        home_stats = api_football.extract_goal_averages(home_stats_raw)
        away_stats = api_football.extract_goal_averages(away_stats_raw)
        lh, la = prediction_engine.expected_goals(home_stats, away_stats)
        result = prediction_engine.simulate_match(lh, la)
        result.pop("_home_goals"); result.pop("_away_goals")
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur en récupérant les données : {e}")


@app.post("/predict/coupon")
async def predict_coupon(req: CouponPredictionRequest):
    """
    Probabilité RÉELLE (simulée) qu'un coupon entier passe — à comparer honnêtement
    à la cote totale annoncée par un bookmaker.
    """
    try:
        matches = []
        for pick in req.picks:
            home_raw = await api_football.get_team_statistics(pick.home_team_id, pick.league_id, pick.season)
            away_raw = await api_football.get_team_statistics(pick.away_team_id, pick.league_id, pick.season)
            home_stats = api_football.extract_goal_averages(home_raw)
            away_stats = api_football.extract_goal_averages(away_raw)
            lh, la = prediction_engine.expected_goals(home_stats, away_stats)
            matches.append({"lambda_home": lh, "lambda_away": la, "market": pick.market})
        return prediction_engine.simulate_coupon(matches, n=req.simulations)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur en récupérant les données : {e}")
