from pydantic import BaseModel, Field


class MatchSelection(BaseModel):
    fixture_id: int
    competition: str
    home: str
    away: str
    market: str          # ex: "1N2 domicile", "Plus de 2.5 buts"
    odd: float
    sources: int         # nombre de bookmakers ayant servi à calculer la cote moyenne


class CouponRequest(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    sports: list[str] = Field(default_factory=lambda: ["football"])
    odd_min: float = 3.0
    odd_max: float = 15.0
    max_matches: int = 8


class CouponResponse(BaseModel):
    selections: list[MatchSelection]
    total_odd: float
    warning: str


class MatchPredictionRequest(BaseModel):
    home_team_id: int
    away_team_id: int
    league_id: int
    season: int


class CouponMarketPick(BaseModel):
    home_team_id: int
    away_team_id: int
    league_id: int
    season: int
    market: str  # "home_win" | "draw" | "away_win" | "over_2_5" | "under_2_5" | "btts"


class CouponPredictionRequest(BaseModel):
    picks: list[CouponMarketPick]
    simulations: int = 20000
