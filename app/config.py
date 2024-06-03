import os
import json

SPREADSHEET_DB_ID = os.getenv("SPREADSHEET_DB_ID")
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")
private_key_path = os.getenv("PRIVATE_KEY_PATH")

# デバッグ用のプリント文
print(f"SPREADSHEET_DB_ID: {SPREADSHEET_DB_ID}")
print(f"LINE_NOTIFY_TOKEN: {LINE_NOTIFY_TOKEN}")
print(f"PRIVATE_KEY_PATH: {private_key_path}")

# 環境変数が設定されているか確認
if not SPREADSHEET_DB_ID or not LINE_NOTIFY_TOKEN or not private_key_path:
    raise ValueError("環境変数が正しく設定されていません。")

try:
    # JSONファイルの内容を確認
    with open(private_key_path, "r") as f:
        private_key_content = json.load(f)
    # JSONファイルの内容を一時ファイルに書き込む
    PRIVATE_KEY_PATH = "service_account.json"
    with open(PRIVATE_KEY_PATH, "w") as f:
        json.dump(private_key_content, f)
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    raise ValueError("PRIVATE_KEYの内容が無効なJSONです。") from e
except Exception as e:
    print(f"Error reading file: {e}")
    raise ValueError("PRIVATE_KEY_PATHのファイルを読み込めませんでした。") from e

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
