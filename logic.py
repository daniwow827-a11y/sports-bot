from api import get_team_form


# 📊 перевод коэффициента в вероятность
def odds_to_prob(odds):
    return 1 / odds


# 📈 считаем форму команды
def form_score(results):
    score = 0
    for r in results:
        if r == "W":
            score += 1
        elif r == "L":
            score -= 1
        # ничья = 0
    return score


# 🧠 основной анализ матча
def analyze_match(home, away, home_odds, away_odds):
    try:
        # получаем форму
        home_results = get_team_form(home)
        away_results = get_team_form(away)

        home_form = form_score(home_results)
        away_form = form_score(away_results)

        # вероятность букмекера
        home_prob_book = odds_to_prob(home_odds)
        away_prob_book = odds_to_prob(away_odds)

        # наша модель (простая, но рабочая)
        home_prob = home_prob_book + (home_form * 0.03)
        away_prob = away_prob_book + (away_form * 0.03)

        home_value = home_prob * home_odds
        away_value = away_prob * away_odds

        bets = []

        if home_value > 1:
            bets.append({
                "team": home,
                "odds": home_odds,
                "prob": round(home_prob * 100),
                "value": home_value
            })

        if away_value > 1:
            bets.append({
                "team": away,
                "odds": away_odds,
                "prob": round(away_prob * 100),
                "value": away_value
            })

        return bets

    except Exception as e:
        print("Ошибка в analyze_match:", e)
        return []


# 🛡️ анти-слив фильтр
def is_safe_bet(bet):
    try:
        # слишком низкий коэффициент (невыгодно)
        if bet['odds'] < 1.4:
            return False

        # слишком высокий (риск)
        if bet['odds'] > 3.5:
            return False

        # нет value
        if bet['value'] < 1.05:
            return False

        return True

    except:
        return False
