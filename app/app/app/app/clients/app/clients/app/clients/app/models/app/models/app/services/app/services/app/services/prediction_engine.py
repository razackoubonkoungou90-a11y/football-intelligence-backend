"""
Moteur de prédiction : buts attendus (Poisson) + simulation Monte Carlo.

Pourquoi Monte Carlo plutôt que multiplier les cotes ?
Multiplier des cotes suppose juste "probabilité = 1 / cote" pour chaque match, indépendamment.
Ici on simule chaque match des milliers de fois à partir de ses buts attendus, PUIS on regarde,
sur les mêmes tirages, combien de fois TOUTES les sélections du coupon tombent ensemble.
Résultat : une probabilité réelle estimée pour le coupon entier — souvent très différente
(et presque toujours plus basse) que ce que la cote totale laisse penser.
"""
import numpy as np


def expected_goals(home_stats: dict, away_stats: dict) -> tuple[float, float]:
    """
    Estime les buts attendus (lambda) pour chaque équipe à partir de leurs moyennes.
    Approche simple : moyenne entre l'attaque de l'un et la défense de l'autre.
    """
    lambda_home = (home_stats["scored_home"] + away_stats["conceded_away"]) / 2 or 0.1
    lambda_away = (away_stats["scored_away"] + home_stats["conceded_home"]) / 2 or 0.1
    return round(lambda_home, 2), round(lambda_away, 2)


def simulate_match(lambda_home: float, lambda_away: float, n: int = 20000, seed: int | None = None) -> dict:
    """Simule n matchs indépendants et retourne des probabilités empiriques pour les marchés courants."""
    rng = np.random.default_rng(seed)
    home_goals = rng.poisson(lambda_home, n)
    away_goals = rng.poisson(lambda_away, n)
    total_goals = home_goals + away_goals

    return {
        "lambda_home": lambda_home,
        "lambda_away": lambda_away,
        "home_win": round(float(np.mean(home_goals > away_goals)), 4),
        "draw": round(float(np.mean(home_goals == away_goals)), 4),
        "away_win": round(float(np.mean(home_goals < away_goals)), 4),
        "over_2_5": round(float(np.mean(total_goals > 2.5)), 4),
        "under_2_5": round(float(np.mean(total_goals <= 2.5)), 4),
        "btts": round(float(np.mean((home_goals > 0) & (away_goals > 0))), 4),
        "_home_goals": home_goals,  # gardé en interne pour la simulation jointe du coupon
        "_away_goals": away_goals,
    }


def simulate_coupon(matches: list[dict], n: int = 20000, seed: int | None = None) -> dict:
    """
    matches : liste de {"lambda_home", "lambda_away", "market"} où market est l'un de
              "home_win", "draw", "away_win", "over_2_5", "under_2_5", "btts".
    Simule TOUS les matchs
