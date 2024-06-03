import os
import json
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

SPREADSHEET_DB_ID = st.secrets["SPREADSHEET_DB_ID"]
LINE_NOTIFY_TOKEN = st.secrets["LINE_NOTIFY_TOKEN"]
PRIVATE_KEY_INFO = st.secrets["PRIVATE_KEY"]

if not SPREADSHEET_DB_ID or not LINE_NOTIFY_TOKEN or not PRIVATE_KEY_INFO:
    raise ValueError("環境変数が正しく設定されていません。")

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
