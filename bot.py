import requests
import pandas as pd
from telegram import Bot
from config import TOKEN, CHANNEL_ID, API_KEY
import schedule
import time
from flask import Flask
import threading

bot = Bot(token=TOKEN)

# =========================
# ФУНКЦИИ
# =========================

def odds_to_prob(odds):
    return 1 / odds

def analyze_match(home, away, home_odds, away_odds):
    home_prob = odds_to_prob(home_odds)
    away_prob = odds_to_prob(away_odds)

    home_value = home_prob * home_odds
    away_value = away_prob * away_odds

    bets = []

    if home_value > 1.05:
        bets.append({
            "team": home,
            "odds": home_odds,
            "prob": int(home_prob * 100),
            "value": home_value
        })

    if away_value > 1.05:
        bets.append({
            "team": away,
            "odds": away_odds,
            "prob": int(away_prob * 100),
            "value": away_value
        })

    return bets

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
    try:
        df = pd.read_csv("stats.csv")
    except:
        return 0

    profit = 0
    bets = 0

    for _, r in df.iterrows():
        if r['result'] == "win":
            profit += r['odds'] - 1
            bets += 1
        elif r['result'] == "lose":
            profit -= 1
            bets += 1

    return round((profit / bets * 100), 2) if bets else 0

# =========================
# ПОЛУЧЕНИЕ МАТЧЕЙ
# =========================

def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    return requests.get(url).json()

def get_top_bets():
    matches = get_matches()
    all_bets = []

    for m in matches:
        try:
            home = m['home_team']
            away = m['away_team']

            outcomes = m['bookmakers'][0]['markets'][0]['outcomes']
            home_odds = outcomes[0]['price']
            away_odds = outcomes[1]['price']

            bets = analyze_match(home, away, home_odds, away_odds)

            for b in bets:
                if 1.4 < b['odds'] < 3.5:
                    b['match'] = f"{home} vs {away}"
                    all_bets.append(b)

        except:
            continue

    all_bets.sort(key=lambda x: x['value'], reverse=True)
    return all_bets[:3]

# =========================
# ОТПРАВКА
# =========================

def send_prediction():
    bets = get_top_bets()

    if not bets:
        print("Нет ставок")
        return

    text = "🔥 AI TOP PICKS\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for i, b in enumerate(bets):
        text += f"""
{medals[i]} {b['match']}
✅ {b['team']}
💰 Коэф: {b['odds']}
📊 Вероятность: {b['prob']}%
"""

        save_bet(b['match'], b['team'], b['odds'], b['prob'], b['value'])

    roi = calculate_roi()

    text += f"\n📈 ROI: {roi}%"

    bot.send_message(chat_id=CHANNEL_ID, text=text)

# =========================
# АВТОЗАПУСК
# =========================

def run_bot():
    send_prediction()
    schedule.every().day.at("12:00").do(send_prediction)

    while True:
        schedule.run_pending()
        time.sleep(60)

# =========================
# FLASK (для Render)
# =========================

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# =========================
# ЗАПУСК
# =========================

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
