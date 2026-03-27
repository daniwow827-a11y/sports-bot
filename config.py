from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL")
API_KEY = os.getenv("API_KEY")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")