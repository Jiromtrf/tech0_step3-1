import os
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from config import SPREADSHEET_DB_ID, PRIVATE_KEY_PATH, scopes

def get_credentials():
    return Credentials.from_service_account_file(PRIVATE_KEY_PATH, scopes=scopes)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def create_user():
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_DB_ID).worksheet("ユーザーDB")
    if not sheet.get_all_records():
        sheet.append_row(["username", "password"])

def add_user(username, password):
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_DB_ID).worksheet("ユーザーDB")
    sheet.append_row([username, password])

def login_user(username, password):
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_DB_ID).worksheet("ユーザーDB")
    records = sheet.get_all_records()
    user_df = pd.DataFrame(records)
    result = user_df[(user_df['username'] == username) & (user_df['password'] == password)]
    return result

def main():
    st.title("ログイン")
    if st.session_state['logged_in']:
        st.write(f"こんにちは、{st.session_state['username']} さん")
        st.write("[物件検索ページへ移動](pages/02_物件検索.py)")
        st.write("[マイページへ移動](pages/04_お気に入り一覧.py)")
    else:
        st.subheader("ログイン画面です")
        username = st.text_input("ユーザー名を入力してください")
        password = st.text_input("パスワードを入力してください", type='password')
        if st.button("ログイン"):
            create_user()
            hashed_pswd = make_hashes(password)
            result = login_user(username, check_hashes(password, hashed_pswd))
            if not result.empty:
                st.success(f"{username}さんでログインしました")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
            else:
                st.warning("ユーザー名かパスワードが間違っています")
        st.write("[初めてのご利用の場合は新規登録ページへ移動](pages/01_新規登録.py)")

if __name__ == '__main__':
    main()
