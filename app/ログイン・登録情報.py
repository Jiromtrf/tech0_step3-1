import streamlit as st
from datetime import datetime
import pandas as pd
import re
import smtplib
from validate_email import validate_email
import gspread
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe
from gspread_dataframe import set_with_dataframe
from dotenv import load_dotenv
import os
from PIL import Image

# 環境変数の読み込み
load_dotenv(r'C:\Users\kouji\Desktop\tech0\step3\step3-1\.env.gspread')

# 環境変数から認証情報を取得
SPREADSHEET_User_ID = os.getenv("SPREADSHEET_User_ID")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")

# googleスプレッドシートの認証 jsonファイル読み込み(key値はGCPから取得)
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


SP_SHEET_KEY = SPREADSHEET_User_ID # d/〇〇/edit の〇〇部分
sh  = gc.open_by_key(SP_SHEET_KEY)

# 取得した不動産データの書き込み
SP_SHEET_wr     = 'user' # sheet名
worksheet_wr = sh.worksheet(SP_SHEET_wr) # シートのデータ取得

# ヘッダー画像の表示
header_image = Image.open(r"C:\Users\kouji\Desktop\tech0\step3\step3-1\app\image\アプリバナー.png")
st.image(header_image, use_column_width=True)

# サイドバーの設定
name = st.sidebar.text_input("お名前", key="sidebar_name")
email = st.sidebar.text_input("メールアドレス", key="sidebar_email")
password = st.sidebar.text_input("パスワード", type="password", key="sidebar_password")

# データ取得関数
def get_records():
    return worksheet_wr.get_all_records()

# グローバル変数としてrecordsを定義
records = get_records()

# ユーザー情報を保存する変数
user_id = ""
location1 = ""
location2 = ""

if st.sidebar.button("sign in", key="sidebar_signin"):
    # 登録されているかチェック
    user_record = next((record for record in records if record.get("メールアドレス") == email), None)
    
    if user_record:
        st.sidebar.success("ログインしました")
        user_id = user_record["ID"]
        name = user_record["お名前"]
        email = user_record["メールアドレス"]
        location1 = user_record.get("勤務地1", "")
        location2 = user_record.get("勤務地2", "")
    else:
        # 新規登録
        user_id = len(records) + 1
        worksheet_wr.append_row([user_id, name, email, password, location1, location2])
        st.sidebar.success("新規登録が完了しました")
        # recordsを更新
        records = get_records()

# メインコンテンツの入力フィールド
id_value = st.text_input("ID", value=user_id, key="main_id")
name_value = st.text_input("お名前", value=name, key="main_name")
email_value = st.text_input("メールアドレス", value=email, key="main_email")
location1_value = st.text_input("勤務地1", value=location1, key="main_location1")
location2_value = st.text_input("勤務地2", value=location2, key="main_location2")

# 登録ボタンの設置
if st.button("登録", key="main_register"):
    # email_valueを使用して登録されているユーザーのレコードを取得
    cell = worksheet_wr.find(email_value)
    if cell:
        # 更新
        worksheet_wr.update_cell(cell.row, 2, name_value)  # 5は勤務地1のカラム
        worksheet_wr.update_cell(cell.row, 5, location1_value)  # 5は勤務地1のカラム
        worksheet_wr.update_cell(cell.row, 6, location2_value)  # 6は勤務地2のカラム
        st.success("登録情報が更新されました")
    else:
        st.error("ユーザーが見つかりません。サインインしてください。")

# メールアドレス形式を検証する関数
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None