import os
import streamlit as st

SPREADSHEET_DB_ID = st.secrets["SPREADSHEET_DB_ID"]
LINE_NOTIFY_TOKEN = st.secrets["LINE_NOTIFY_TOKEN"]
PRIVATE_KEY_PATH = st.secrets["PRIVATE_KEY_PATH"]

if not SPREADSHEET_DB_ID or not LINE_NOTIFY_TOKEN or not PRIVATE_KEY_PATH:
    raise ValueError("環境変数が正しく設定されていません。")

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
