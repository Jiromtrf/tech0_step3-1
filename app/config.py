import os
import json

SPREADSHEET_DB_ID = os.getenv("SPREADSHEET_DB_ID")
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")
private_key_content = os.getenv("PRIVATE_KEY")

print(f"SPREADSHEET_DB_ID: {SPREADSHEET_DB_ID}")
print(f"LINE_NOTIFY_TOKEN: {LINE_NOTIFY_TOKEN}")
print(f"PRIVATE_KEY: {private_key_content is not None}")

if not SPREADSHEET_DB_ID or not LINE_NOTIFY_TOKEN or not private_key_content:
    raise ValueError("環境変数が正しく設定されていません。")

# JSONファイルの内容を一時ファイルに書き込む
PRIVATE_KEY_PATH = "service_account.json"
with open(PRIVATE_KEY_PATH, "w") as f:
    f.write(private_key_content)

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
