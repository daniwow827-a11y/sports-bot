import requests
import asyncio
import schedule
import time
from telegram import Bot
from config import TOKEN, CHANNEL_ID, API_KEY
from logic import analyze_match, is_safe_bet
from stats import save_bet, calculate_roi
from leagues import TOP_LEAGUES

bot = Bot(token=TOKEN)


# 📥 Получаем матчи
def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    return requests.get(url).json()


# 🧠 собираем лучшие ставки
def get_top_bets():
    matches = get_matches()
    all_bets = []

    for match in matches:
        try:
            league = match['sport_title']

            if not any(top in league for top in TOP_LEAGUES):
                continue

            home = match['home_team']
            away = match['away_team']

            outcomes = match['bookmakers'][0]['markets'][0]['outcomes']

            home_odds = outcomes[0]['price']
            away_odds = outcomes[1]['price']

            bets = analyze_match(home, away, home_odds, away_odds)

            for bet in bets:
                if is_safe_bet(bet):
                    bet['match'] = f"{home} vs {away}"
                    all_bets.append(bet)

        except Exception as e:
            print("Ошибка:", e)
            continue

    all_bets.sort(key=lambda x: x['value'], reverse=True)

    return all_bets[:3]


# 📢 отправка
async def send_prediction():
    print("Запуск прогноза...")

    bets = get_top_bets()

    if not bets:
        print("Нет ставок")
        return

    text = "🔥 AI TOP PICKS\n\n"
    emojis = ["🥇", "🥈", "🥉"]

    for i, bet in enumerate(bets):
        text += f"""
{emojis[i]} {bet['match']}
✅ {bet['team']}

💰 Коэф: {bet['odds']}
📊 Вероятность: {bet['prob']}%
📈 Value: {round(bet['value'], 2)}
"""

        save_bet(
            bet['match'],
            bet['team'],
            bet['odds'],
            bet['prob'],
            bet['value']
        )

    roi = calculate_roi()

    text += f"""

📊 Статистика:
ROI: {round(roi, 2)}%
"""

    await bot.send_message(chat_id=CHANNEL_ID, text=text)

    print("Отправлено!")


# ⏰ планировщик
def run_scheduler():
    schedule.every().day.at("12:00").do(lambda: asyncio.run(send_prediction()))

    print("Бот запущен и ждёт расписание...")

    while True:
        schedule.run_pending()
        time.sleep(60)


# ▶️ старт
if __name__ == "__main__":
    run_scheduler()
