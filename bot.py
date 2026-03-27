import requests
from telegram import Bot
from config import *
from logic import analyze
from stats import save_bet, calculate_roi

bot = Bot(token=TOKEN)

def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    return requests.get(url).json()

def run():
    matches = get_matches()
    bets = []

    for m in matches:
        try:
            home = m['home_team']
            away = m['away_team']

            outcomes = m['bookmakers'][0]['markets'][0]['outcomes']
            home_odds = outcomes[0]['price']
            away_odds = outcomes[1]['price']

            res = analyze(home, away, home_odds, away_odds)

            for r in res:
                if r[4] > 1.05:
                    bets.append({
                        "match": f"{home} vs {away}",
                        "team": r[1],
                        "odds": r[2],
                        "prob": int(r[3]*100),
                        "value": r[4]
                    })
        except:
            continue

    bets.sort(key=lambda x: x['value'], reverse=True)
    top = bets[:3]

    text = "🔥 AI PICKS\n\n"

    for i, b in enumerate(top):
        text += f"""
{i+1}) {b['match']}
✅ {b['team']}
💰 {b['odds']}
📊 {b['prob']}%
"""

        save_bet(b['match'], b['team'], b['odds'], b['prob'], b['value'])

    roi = calculate_roi()

    text += f"\nROI: {round(roi,2)}%"

    bot.send_message(chat_id=CHANNEL_ID, text=text)

run()
import schedule, time

schedule.every().day.at("12:00").do(run)

while True:
    schedule.run_pending()
    time.sleep(60)