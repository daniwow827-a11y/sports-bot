from api import get_team_form

def form_score(results):
    score = 0
    for r in results:
        if r == "W":
            score += 1
        elif r == "L":
            score -= 1
    return score

def odds_to_prob(odds):
    return 1 / odds

def analyze(home, away, home_odds, away_odds):
    home_form = form_score(get_team_form(home))
    away_form = form_score(get_team_form(away))

    home_prob = odds_to_prob(home_odds) + home_form * 0.03
    away_prob = odds_to_prob(away_odds) + away_form * 0.03

    home_value = home_prob * home_odds
    away_value = away_prob * away_odds

    return [
        ("home", home, home_odds, home_prob, home_value),
        ("away", away, away_odds, away_prob, away_value)
    ]