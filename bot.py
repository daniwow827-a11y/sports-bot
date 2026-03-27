import requests
import pandas as pd
import asyncio
import os
import random
from telegram import Bot

# Flask для Render
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_web():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_web).start()

# CONFIG
TOKEN = os.getenv("TOKEN")
CHANNEL = os.getenv("CHANNEL")
API_KEY = os.getenv("API_KEY")

bot = Bot(token=TOKEN)

# =========================
# Получение матчей
# =========================
def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h,totals"
    res = requests.get(url)
    data = res.json()

    if isinstance(data, list):
        return data
    return []

# =========================
# Прогноз
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

    if bet_type == "win" and h2h:
        best = min(h2h, key=lambda x: x['price'])
        return f"Победа {best['name']}", best['price'], round((1 / best['price']) * 100)

    if bet_type == "total" and totals:
        t = totals[0]
        return f"{t['name']} {t.get('point', '')}", t['price'], round((1 / t['price']) * 100)

    return None, None, None

# =========================
# ОТПРАВКА СРАЗУ
# =========================
async def send_now():
    data = get_matches()

    if not data:
        print("Нет матчей")
        return

    for match in data:
        if not match.get('bookmakers'):
            continue

        home = match['home_team']
        away = match['away_team']
        bookmaker = match['bookmakers'][0]

        team, odds, confidence = make_prediction(bookmaker)

        if not team:
            continue

        text = f"""
🔥 ТЕСТ ПРОГНОЗ

⚔️ {home} vs {away}

✅ Ставка: {team}
💰 Коэф: {odds}
📊 Уверенность: {confidence}%
"""

        try:
            await bot.send_message(chat_id=CHANNEL, text=text)
            print("ОТПРАВИЛОСЬ ✅")
            return
        except Exception as e:
            print("Ошибка:", e)

    print("Не удалось отправить")

# =========================
# ЗАПУСК СРАЗУ
# =========================
asyncio.run(send_now())
