import pandas as pd

def save_bet(match, team, odds, prob, value):
    df = pd.DataFrame([{
        "match": match,
        "team": team,
        "odds": odds,
        "prob": prob,
        "value": value,
        "result": "pending"
    }])
    df.to_csv("stats.csv", mode='a', header=False, index=False)

def calculate_roi():
    df = pd.read_csv("stats.csv")

    profit = 0
    bets = 0

    for _, r in df.iterrows():
        if r['result'] == "win":
            profit += r['odds'] - 1
            bets += 1
        elif r['result'] == "lose":
            profit -= 1
            bets += 1

    return (profit / bets * 100) if bets else 0