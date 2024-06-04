import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from config import SPREADSHEET_DB_ID, PRIVATE_KEY_PATH, scopes

def get_credentials():
    return Credentials.from_service_account_info(st.secrets["PRIVATE_KEY_PATH"], scopes=scopes)


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

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

def main():
    st.title("サインアップ")
    st.subheader("新しいアカウントを作成します")
    new_user = st.text_input("ユーザー名を入力してください")
    new_password = st.text_input("パスワードを入力してください", type='password')
    if st.button("サインアップ"):
        create_user()
        add_user(new_user, make_hashes(new_password))
        st.success("アカウントの作成に成功しました")
        st.info("ログイン画面からログインしてください")
    st.write("[ログインページへ移動](../ログイン.py)")

if __name__ == '__main__':
    main()
