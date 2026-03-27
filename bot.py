import requests
import pandas as pd
import schedule
import time
from datetime import datetime, timedelta, timezone
import asyncio
import os
import random
from telegram import Bot

# 🔥 Flask для Render
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_web():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_web).start()

# =========================
# CONFIG
# =========================
TOKEN = os.getenv("TOKEN")
CHANNEL = os.getenv("CHANNEL")
API_KEY = os.getenv("API_KEY")

bot = Bot(token=TOKEN)

LAST_FILE = "last_post.txt"

# =========================
# Проверка отправки
# =========================
def already_posted_today():
    if not os.path.exists(LAST_FILE):
        return False

    with open(LAST_FILE, "r") as f:
        last_date = f.read().strip()

    today = datetime.now().strftime("%Y-%m-%d")
    return last_date == today

def mark_posted():
    today = datetime.now().strftime("%Y-%m-%d")

    with open(LAST_FILE, "w") as f:
        f.write(today)

# =========================
# Матчи
# =========================
def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h,totals"
    res = requests.get(url)
    data = res.json()

    if isinstance(data, list):
        return data
    return []

# =========================
# Время
# =========================
def is_good_time(match_time_str):
    match_time = datetime.fromisoformat(match_time_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    diff = match_time - now
    return timedelta(minutes=0) <= diff <= timedelta(hours=4)

# =========================
# Сортировка
# =========================
def sort_by_time(matches):
    return sorted(
        matches,
        key=lambda m: datetime.fromisoformat(m["commence_time"].replace("Z", "+00:00"))
    )

# =========================
# Разные ставки
# =========================
def make_prediction(bookmaker):
    markets = bookmaker['markets']

    h2h = None
    totals = None

    for m in markets:
        if m['key'] == 'h2h':
            h2h = m['outcomes']
        elif m['key'] == 'totals':
            totals = m['outcomes']

    bet_type = random.choice(["win", "total"])

    # Победа
    if bet_type == "win" and h2h:
        best = min(h2h, key=lambda x: x['price'])

        if 1.5 <= best['price'] <= 2.5:
            return f"Победа {best['name']}", best['price'], round((1 / best['price']) * 100)

    # Тотал
    if bet_type == "total" and totals:
        for t in totals:
            if 1.7 <= t['price'] <= 2.2:
                return f"{t['name']} {t.get('point', '')}", t['price'], round((1 / t['price']) * 100)

    return None, None, None

# =========================
# Сохранение
# =========================
def save_stat(home, away, team, odds):
    df = pd.DataFrame([{
        "date": datetime.now(),
        "match": f"{home} vs {away}",
        "prediction": team,
        "odds": odds,
        "result": "pending"
    }])

    df.to_csv("stats.csv", mode='a', header=False, index=False)

# =========================
# Отправка
# =========================
async def send_prediction():
    if already_posted_today():
        print("Сегодня уже был прогноз")
        return

    data = get_matches()

    if not data:
        print("Нет матчей")
        return

    data = sort_by_time(data)

    for match in data:
        if not match.get('bookmakers'):
            continue

        match_time = match.get("commence_time")

        if not match_time or not is_good_time(match_time):
            continue

        home = match['home_team']
        away = match['away_team']

        bookmaker = match['bookmakers'][0]

        team, odds, confidence = make_prediction(bookmaker)

        if not team:
            continue

        start_time = match_time[:16].replace("T", " ")

        text = f"""
🔥 ПРОГНОЗ ДНЯ

⚽ Футбол

⚔️ {home} vs {away}

⏰ Начало: {start_time}

✅ Ставка: {team}
💰 Коэф: {odds}
📊 Уверенность: {confidence}%
"""

        for i in range(3):
            try:
                await bot.send_message(chat_id=CHANNEL, text=text)
                break
            except Exception as e:
                print(f"Ошибка {i+1}: {e}")
                await asyncio.sleep(2)

        save_stat(home, away, team, odds)
        mark_posted()

        print("Прогноз отправлен")

        return

    print("Матч не найден")

# =========================
# запуск
# =========================
def run_async():
    asyncio.run(send_prediction())

schedule.every(10).minutes.do(run_async)

print("БОТ РАБОТАЕТ 24/7 🚀")

while True:
    schedule.run_pending()
    time.sleep(60)
