import requests
from config import API_FOOTBALL_KEY

def get_team_form(team_id):
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"

    headers = {
        'x-apisports-key': API_FOOTBALL_KEY
    }

    res = requests.get(url, headers=headers).json()

    results = []

    for m in res['response']:
        g1 = m['goals']['home']
        g2 = m['goals']['away']

        if g1 > g2:
            results.append("W")
        elif g1 < g2:
            results.append("L")
        else:
            results.append("D")

    return results