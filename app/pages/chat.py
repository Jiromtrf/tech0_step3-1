import os
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from datetime import datetime
import folium
from streamlit_folium import folium_static
import requests
import time

# 環境変数の読み込み
load_dotenv()

# 環境変数から認証情報を取得
SPREADSHEET_chat_ID = os.getenv("SPREADSHEET_chat_ID")
SPREADSHEET_property_ID = os.getenv("SPREADSHEET_property_ID")
SPREADSHEET_rating_ID = os.getenv("SPREADSHEET_rating_ID")  # 評価用スプレッドシートID
SPREADSHEET_user_ID = os.getenv("SPREADSHEET_user_ID")
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")  # LINE Notifyのトークン
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")

chat_SHEET = 'メッセージ記録'  # シート名
property_SHEET = '緯度・経度取得'  # 物件情報シート名
user_SHEET = 'ユーザーお気に入り'  # お気に入り登録情報（property_idで連携）
rating_SHEET = '評価'  # 評価シート名

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

# スプレッドシートとワークシートをキャッシュ
@st.cache_data(ttl=600)  # 10分間キャッシュ
def load_sheets():
    chat_sh = gc.open_by_key(SPREADSHEET_chat_ID).worksheet(chat_SHEET)
    property_sh = gc.open_by_key(SPREADSHEET_property_ID).worksheet(property_SHEET)
    rating_sh = gc.open_by_key(SPREADSHEET_rating_ID).worksheet(rating_SHEET)
    user_sh = gc.open_by_key(SPREADSHEET_user_ID).worksheet(user_SHEET)
    return chat_sh, property_sh, rating_sh, user_sh

chat_sh, property_sh, rating_sh, user_sh = load_sheets()

# ユーザーお気に入りから物件情報を読み込む関数
def load_user_properties():
    records = user_sh.get_all_records()
    return records

# 物件の詳細情報を読み込む関数
def load_property_details(property_id):
    # 物件シートから該当する物件の詳細情報を取得
    property_records = property_sh.get_all_records()
    for record in property_records:
        if record['property_id'] == property_id:
            return record
    return None

# チャットデータを読み込む関数
def load_messages(property_id):
    records = chat_sh.get_all_records()
    if not records:
        return pd.DataFrame()  # チャット記録が空の場合は空のDataFrameを返す
    df = pd.DataFrame(records)
    property_messages = df[df['property_id'] == property_id]  # property_id に基づいてフィルタ
    return property_messages

# チャットデータを保存する関数
def save_message(sender, text, property_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ヘッダー行が既に存在するかをチェック
    if not chat_sh.row_values(1) or chat_sh.row_values(1) != ['timestamp', 'sender', 'text', 'property_id']:
        chat_sh.insert_row(['timestamp', 'sender', 'text', 'property_id'], 1)

    chat_sh.append_row([timestamp, sender, text, property_id])

    # 物件の名称を取得
    property_details = load_property_details(property_id)
    property_name = property_details['名称'] if property_details else "物件名なし"

    # LINE通知を送信
    send_line_notification(sender, text, property_name)  # property_id の代わりに property_name を渡す

# 評価を保存する関数
def save_rating(rater, rating, property_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ヘッダー行が既に存在するかをチェック
    if not rating_sh.row_values(1) or rating_sh.row_values(1) != ['timestamp', 'rater', 'rating', 'property_id']:
        rating_sh.insert_row(['timestamp', 'rater', 'rating', 'property_id'], 1)

    rating_sh.append_row([timestamp, rater, rating, property_id])

# 評価データを読み込む関数
def load_ratings(property_id):
    records = rating_sh.get_all_records()
    if not records:
        return pd.DataFrame()  # 評価記録が空の場合は空のDataFrameを返す
    df = pd.DataFrame(records)
    property_ratings = df[df['property_id'] == property_id]  # property_id に基づいてフィルタ
    return property_ratings

# 最新の評価を取得する関数
def get_latest_ratings(ratings_df):
    # timestamp列が存在しない場合を考慮して、エラーが発生しないように修正
    if 'timestamp' in ratings_df.columns:
        latest_ratings = ratings_df.sort_values(by='timestamp').drop_duplicates(subset='rater', keep='last')
        return latest_ratings
    else:
        return pd.DataFrame()  # エラーが発生した場合は空のDataFrameを返す

# LINE通知を送信する関数
def send_line_notification(sender, text, property_name):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"
    }
    payload = {
        "message": f"{sender}さんから新しいメッセージ: {text} (物件名: {property_name})"
    }
    requests.post(url, headers=headers, data=payload)

# ユーザーインターフェースの構築
st.title('共有スペース')

# お気に入り物件情報を読み込む
user_properties = load_user_properties()
favorite_property_ids = [record['property_id'] for record in user_properties]

# タブで表示する物件名を取得
property_names = []
properties = []
for property_id in favorite_property_ids:
    property_details = load_property_details(property_id)
    if property_details:
        property_names.append(property_details['名称'])
        properties.append(property_details)

# 物件情報をタブで表示
tabs = st.tabs(property_names)

for i, property_details in enumerate(properties):
    with tabs[i]:
        property_name = property_details['名称']

        # 物件の詳細情報を表示
        if property_details:
            st.write(f"家賃: {property_details.get('家賃', '情報なし')} 万円")  # 家賃情報を表示
            st.write(f"間取り: {property_details.get('間取り', '情報なし')}")  # 間取り情報を表示
            st.write(f"面積: {property_details.get('面積', '情報なし')}m2")
            st.write(f"最寄り駅: {property_details.get('アクセス①1駅名', '情報なし')}")  # 駅情報を表示
            st.write(f"築年数: {property_details.get('築年数', '情報なし')}年")
            st.write(f"物件詳細URL: {property_details.get('物件詳細URL', '情報なし')}")

            col1, col2 = st.columns(2)
            with col1:
                property_image_url = property_details.get("物件画像URL", "")
                if property_image_url:
                    st.image(property_image_url, use_column_width=True, width=300)  # 物件画像を表示
                else:
                    st.write("物件画像が見つかりません")

            with col2:
                floor_plan_image_url = property_details.get("間取画像URL", "")
                if floor_plan_image_url:
                    st.image(floor_plan_image_url, use_column_width=True, width=300)  # 間取り画像を表示
                else:
                    st.write("間取り画像が見つかりません")

            # 地図を表示 (緯度と経度を使用)
            lat = property_details.get("緯度", None)
            lon = property_details.get("経度", None)
            if lat and lon:
                map_center = [lat, lon]
                m = folium.Map(location=map_center, zoom_start=15)
                folium.Marker(
                    location=[lat, lon],
                    popup=property_details["名称"]
                ).add_to(m)
                folium_static(m)
            else:
                st.write("地図情報が見つかりません")

        st.divider()

        # メッセージと評価の名前入力フィールドを作成
        sender = st.text_input('名前', key=f'sender_{i}')

        # メッセージと評価の入力フォームを左右に配置
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(':left_speech_bubble:コメント')
            text = st.text_input('内容', key=f'text_{i}')

            # ボタンがクリックされた時の処理
            if st.button('送信', key=f'send_message_{i}'):
                if sender and text:
                    property_id = property_details['property_id']
                    save_message(sender, text, property_id)
                    st.experimental_rerun()  # ページを再読み込みして入力欄をリセット

        with col2:
            st.subheader(':+1:評価')
            rating = st.slider('', 1.0, 5.0, step=0.5, value=3.0, key=f'rating_{i}')  # 0.5刻みで選ぶように設定

            # ボタンがクリックされた時の処理
            if st.button('送信', key=f'send_rating_{i}'):
                if sender and rating:
                    property_id = property_details['property_id']
                    save_rating(sender, rating, property_id)
                    st.success('評価が保存されました！')

            # 評価の表示
            if property_details:
                property_id = property_details['property_id']
                property_ratings = load_ratings(property_id)
                latest_ratings = get_latest_ratings(property_ratings)
                for index, row in latest_ratings.iterrows():
                    st.write(f"{row['rater']}さんの評価：{row['rating']}")

        # チャットの表示
        if property_details:
            property_id = property_details['property_id']
            property_messages = load_messages(property_id)
            for index, row in property_messages.iterrows():
                st.markdown(
                    f"""
                    <div style="background-color: #fdede4; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                        <div><strong>{row["sender"]}:</strong><br>{row["text"]}</div>
                        <div style="font-size: smaller; color: gray; text-align: right;">{row["timestamp"]}</div>
                    </div>
                    """, unsafe_allow_html=True
                )
        else:
            st.write("コメントを表示する")
