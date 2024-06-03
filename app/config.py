import os
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_DB_ID = os.getenv("SPREADSHEET_DB_ID")
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")

if not SPREADSHEET_DB_ID or not LINE_NOTIFY_TOKEN or not PRIVATE_KEY_PATH:
    raise ValueError("環境変数が正しく設定されていません。")

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

