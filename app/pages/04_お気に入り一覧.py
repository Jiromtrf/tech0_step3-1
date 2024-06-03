import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from config import SPREADSHEET_DB_ID, PRIVATE_KEY_PATH, scopes

def get_credentials():
    return Credentials.from_service_account_file(PRIVATE_KEY_PATH, scopes=scopes)

def load_data_from_gsheet(spreadsheet_id, sheet_name):
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def get_favorite_properties(username):
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_DB_ID).worksheet("お気に入りDB")
    records = sheet.get_all_records()
    fav_df = pd.DataFrame(records)
    properties = fav_df[fav_df['username'] == username]['property_id'].tolist()
    return properties

def remove_favorite_property(username, property_id):
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_DB_ID).worksheet("お気に入りDB")
    records = sheet.get_all_records()
    fav_df = pd.DataFrame(records)
    fav_df = fav_df[(fav_df['username'] != username) | (fav_df['property_id'] != property_id)]
    sheet.clear()
    sheet.append_row(["username", "property_id"])
    for index, row in fav_df.iterrows():
        sheet.append_row([row['username'], row['property_id']])

def main():
    st.title("お気に入り一覧")

    if not st.session_state['logged_in']:
        st.warning("ログインしてください")
        st.write("[ログインページへ移動](../ログイン.py)")
        return

    df = load_data_from_gsheet(SPREADSHEET_DB_ID, "物件DB")

    favorite_properties = get_favorite_properties(st.session_state['username'])
    if favorite_properties:
        st.write("お気に入り物件:")
        for property_id in favorite_properties:
            property_data = df[df.index == property_id]
            if not property_data.empty:
                st.write(property_data[['名称', 'アドレス', '家賃', '間取り', '階数']])
                if pd.notnull(property_data.iloc[0]['物件画像URL']) and pd.notnull(property_data.iloc[0]['間取画像URL']):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(property_data.iloc[0]['物件画像URL'], width=300)
                    with col2:
                        st.image(property_data.iloc[0]['間取画像URL'], width=300)
                elif pd.notnull(property_data.iloc[0]['物件画像URL']):
                    st.image(property_data.iloc[0]['物件画像URL'], width=300)
                elif pd.notnull(property_data.iloc[0]['間取画像URL']):
                    st.image(property_data.iloc[0]['間取画像URL'], width=300)
                if st.button(f"お気に入り解除", key=f"remove_{property_id}"):
                    remove_favorite_property(st.session_state['username'], property_id)
                    st.success(f"{property_data.iloc[0]['名称']}をお気に入りから解除しました")

if __name__ == '__main__':
    main()
