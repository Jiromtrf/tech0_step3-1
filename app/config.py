import os
import json
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

SPREADSHEET_DB_ID = st.secrets["SPREADSHEET_DB_ID"]
LINE_NOTIFY_TOKEN = st.secrets["LINE_NOTIFY_TOKEN"]
PRIVATE_KEY_PATH = {
    "type": st.secrets["PRIVATE_KEY_PATH"]["type"],
    "project_id": st.secrets["PRIVATE_KEY_PATH"]["project_id"],
    "private_key_id": st.secrets["PRIVATE_KEY_PATH"]["private_key_id"],
    "private_key": st.secrets["PRIVATE_KEY_PATH"]["private_key"].replace("\\n", "\n"),
    "client_email": st.secrets["PRIVATE_KEY_PATH"]["client_email"],
    "client_id": st.secrets["PRIVATE_KEY_PATH"]["client_id"],
    "auth_uri": st.secrets["PRIVATE_KEY_PATH"]["auth_uri"],
    "token_uri": st.secrets["PRIVATE_KEY_PATH"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["PRIVATE_KEY_PATH"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["PRIVATE_KEY_PATH"]["client_x509_cert_url"],
    "universe_domain": st.secrets["PRIVATE_KEY_PATH"]["universe_domain"]
}

if not SPREADSHEET_DB_ID or not LINE_NOTIFY_TOKEN or not PRIVATE_KEY_PATH:
    raise ValueError("環境変数が正しく設定されていません。")

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
