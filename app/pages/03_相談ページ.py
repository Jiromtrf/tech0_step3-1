import os
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import folium
from streamlit_folium import folium_static
import requests
from config import SPREADSHEET_DB_ID, LINE_NOTIFY_TOKEN, PRIVATE_KEY_PATH, scopes

def get_credentials():
    return Credentials.from_service_account_info(PRIVATE_KEY_PATH, scopes=scopes)

def load_sheets():
    creds = get_credentials()
    client = gspread.authorize(creds)
    chat_sh = client.open_by_key(SPREADSHEET_DB_ID).worksheet('チャットデータDB')
    property_sh = client.open_by_key(SPREADSHEET_DB_ID).worksheet('物件DB')
    rating_sh = client.open_by_key(SPREADSHEET_DB_ID).worksheet('評価DB')
    user_sh = client.open_by_key(SPREADSHEET_DB_ID).worksheet('お気に入りDB')
    return chat_sh, property_sh, rating_sh, user_sh

chat_sh, property_sh, rating_sh, user_sh = load_sheets()

def load_user_properties(username):
    records = user_sh.get_all_records()
    user_properties = [record for record in records if record['username'] == username]
    return user_properties

def load_property_details(property_id):
    property_records = property_sh.get_all_records()
    for record in property_records:
        if record['property_id'] == property_id:
            return record
    return None

def load_messages(property_id):
    records = chat_sh.get_all_records()
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    property_messages = df[df['property_id'] == property_id]
    return property_messages

def save_message(sender, text, property_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not chat_sh.row_values(1) or chat_sh.row_values(1) != ['timestamp', 'sender', 'text', 'property_id']:
        chat_sh.insert_row(['timestamp', 'sender', 'text', 'property_id'], 1)
    chat_sh.append_row([timestamp, sender, text, property_id])
    property_details = load_property_details(property_id)
    property_name = property_details['名称'] if property_details else "物件名なし"
    response = send_line_notification(sender, text, property_name)
    st.write("LINE通知のレスポンス:")
    st.write(response.status_code)
    st.write(response.text)

def save_rating(rater, rating, property_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not rating_sh.row_values(1) or rating_sh.row_values(1) != ['timestamp', 'rater', 'rating', 'property_id']:
        rating_sh.insert_row(['timestamp', 'rater', 'rating', 'property_id'], 1)
    rating_sh.append_row([timestamp, rater, rating, property_id])

def load_ratings(property_id):
    records = rating_sh.get_all_records()
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    property_ratings = df[df['property_id'] == property_id]
    return property_ratings

def get_latest_ratings(ratings_df):
    if 'timestamp' in ratings_df.columns:
        latest_ratings = ratings_df.sort_values(by='timestamp').drop_duplicates(subset='rater', keep='last')
        return latest_ratings
    else:
        return pd.DataFrame()

def send_line_notification(sender, text, property_name):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"
    }
    payload = {
        "message": f"{sender}さんから新しいメッセージ: {text} (物件名: {property_name})"
    }
    response = requests.post(url, headers=headers, data=payload)
    return response

st.title('共有スペース')

if not st.session_state.get('logged_in'):
    st.warning("ログインしてください")
    st.write("[ログインページへ移動](../ログイン.py)")
    st.stop()

username = st.session_state.get('username')

user_properties = load_user_properties(username)
favorite_property_ids = [record['property_id'] for record in user_properties]

property_names = []
properties = []
for property_id in favorite_property_ids:
    property_details = load_property_details(property_id)
    if property_details:
        property_names.append(property_details['名称'])
        properties.append(property_details)

tabs = st.tabs(property_names)

for i, property_details in enumerate(properties):
    with tabs[i]:
        property_name = property_details['名称']
        if property_details:
            st.write(f"家賃: {property_details.get('家賃', '情報なし')} 万円")
            st.write(f"間取り: {property_details.get('間取り', '情報なし')}")
            st.write(f"面積: {property_details.get('面積', '情報なし')}m2")
            st.write(f"最寄り駅: {property_details.get('アクセス①1駅名', '情報なし')}")
            st.write(f"築年数: {property_details.get('築年数', '情報なし')}年")
            st.write(f"物件詳細URL: {property_details.get('物件詳細URL', '情報なし')}")
            col1, col2 = st.columns(2)
            with col1:
                property_image_url = property_details.get("物件画像URL", "")
                if property_image_url:
                    st.image(property_image_url, use_column_width=True, width=300)
                else:
                    st.write("物件画像が見つかりません")
            with col2:
                floor_plan_image_url = property_details.get("間取画像URL", "")
                if floor_plan_image_url:
                    st.image(floor_plan_image_url, use_column_width=True, width=300)
                else:
                    st.write("間取り画像が見つかりません")
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
        sender = st.text_input('名前', key=f'sender_{i}')
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(':left_speech_bubble:コメント')
            text = st.text_input('内容', key=f'text_{i}')
            if st.button('送信', key=f'send_message_{i}'):
                if sender and text:
                    property_id = property_details['property_id']
                    save_message(sender, text, property_id)
                    st.experimental_rerun()
        with col2:
            st.subheader(':+1:評価')
            rating = st.slider('', 1.0, 5.0, step=0.5, value=3.0, key=f'rating_{i}')
            if st.button('送信', key=f'send_rating_{i}'):
                if sender and rating:
                    property_id = property_details['property_id']
                    save_rating(sender, rating, property_id)
                    st.success('評価が保存されました！')
            if property_details:
                property_id = property_details['property_id']
                property_ratings = load_ratings(property_id)
                latest_ratings = get_latest_ratings(property_ratings)
                for index, row in latest_ratings.iterrows():
                    st.write(f"{row['rater']}さんの評価：{row['rating']}")
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
