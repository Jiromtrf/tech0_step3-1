import os
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
from dotenv import load_dotenv
from datetime import datetime

# 環境変数の読み込み
load_dotenv(r'C:\Users\kouji\Desktop\tech0\step3\step3-1\.env.gspread')

# 環境変数から認証情報を取得
SPREADSHEET_chat_ID = os.getenv("SPREADSHEET_chat_ID")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
chat_SHEET = 'メッセージ記録'  # シート名

# Googleスプレッドシートの認証 jsonファイル読み込み (key値はGCPから取得)
SP_CREDENTIAL_FILE = PRIVATE_KEY_PATH

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    SP_CREDENTIAL_FILE,
    scopes=scopes
)
gc = gspread.authorize(credentials)

SP_SHEET_KEY = SPREADSHEET_chat_ID  # d/〇〇/edit の〇〇部分
sh = gc.open_by_key(SP_SHEET_KEY).worksheet(chat_SHEET)

# チャットデータを読み込む関数
def load_messages():
    records = sh.get_all_records()
    return records

# チャットデータを保存する関数
def save_message(sender, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sh.append_row([timestamp, sender, text])

# 初期化
if 'messages' not in st.session_state:
    st.session_state['messages'] = load_messages()

# 新しいメッセージを追加する関数
def add_message(sender, text):
    save_message(sender, text)
    st.session_state['messages'] = load_messages()

# カスタムCSSを追加
st.markdown(
    """
    <style>
    .chat-container {
        height: 300px;
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 10px;
        background-color: #f9f9f9;
    }
    .chat-message {
        margin-bottom: 10px;
        padding: 5px;
        border-radius: 5px;
        background-color: #e0e0e0;
    }
    .chat-timestamp {
        font-size: 0.8em;
        color: gray;
        text-align: right;
    }
    .chat-sender {
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True
)

# ユーザーインターフェースの構築
st.title('お気に入り')

# メッセージ入力フォーム
st.subheader('メッセージを送信')
sender = st.text_input('名前', key='sender')
text = st.text_input('メッセージ', key='text')

# ボタンがクリックされた時の処理
if st.button('送信'):
    if sender and text:
        add_message(sender, text)
        st.experimental_rerun()  # ページを再読み込みして入力欄をリセット

# チャットの表示
st.subheader('チャット欄▽')
chat_container = st.container()
with chat_container:
    for msg in st.session_state['messages']:
        st.markdown(
            f"""
            <div class="chat-message">
                <div class="chat-sender">{msg.get("sender", "Unknown")}</div>
                <div>{msg.get("text", "")}</div>
                <div class="chat-timestamp">{msg.get("timestamp", "")}</div>
            </div>
            """, unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
