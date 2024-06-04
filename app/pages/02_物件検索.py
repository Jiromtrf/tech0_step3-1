import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import folium
from streamlit_folium import folium_static
import googlemaps
from config import SPREADSHEET_DB_ID, PRIVATE_KEY_PATH, GOOGLE_MAPS_API_KEY, scopes

def get_credentials():
    return Credentials.from_service_account_info(PRIVATE_KEY_PATH, scopes=scopes)

def load_data_from_gsheet(spreadsheet_id, sheet_name):
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def preprocess_dataframe(df):
    df['家賃'] = pd.to_numeric(df['家賃'], errors='coerce')
    df = df.dropna(subset=['家賃'])
    return df

def make_clickable(url, name):
    return f'<a target="_blank" href="{url}">{name}</a>'

def calculate_distance_and_time(gmaps, start_coords, end_coords):
    try:
        result = gmaps.distance_matrix(start_coords, end_coords, mode="transit")
        st.write(f"Debug: Google Maps API response: {result}")  # レスポンスを表示
        
        if 'rows' in result and result['rows']:
            elements = result['rows'][0]['elements']
            if elements and 'distance' in elements[0] and 'duration' in elements[0]:
                distance = elements[0]['distance']['text']
                duration = elements[0]['duration']['text']
                return distance, duration
        return None, None
    except googlemaps.exceptions.ApiError as e:
        st.error(f"Google Maps API error: {e}")
        return None, None
    except Exception as e:
        st.error(f"Error calculating distance and time: {e}")
        return None, None


def create_map(filtered_df, workplace_coords, show_supermarkets, supermarket_df=None, show_convenience_stores=False, convenience_store_df=None, show_banks=False, bank_df=None, show_cafes=False, cafe_df=None):
    map_center = [filtered_df['緯度'].mean(), filtered_df['経度'].mean()]
    m = folium.Map(location=map_center, zoom_start=12)
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    
    for idx, row in filtered_df.iterrows():
        if pd.notnull(row['緯度']) and pd.notnull(row['経度']):
            popup_html = f"""
            <b>名称:</b> {row['名称']}<br>
            <b>アドレス:</b> {row['アドレス']}<br>
            <b>家賃:</b> {row['家賃']}万円<br>
            <b>間取り:</b> {row['間取り']}<br>
            <a href="{row['物件詳細URL']}" target="_blank">物件詳細</a>
            """
            if workplace_coords:
                distance, duration = calculate_distance_and_time(gmaps, workplace_coords, (row['緯度'], row['経度']))
                if distance and duration:
                    popup_html += f"""
                    <b>勤務地までの距離:</b> {distance}<br>
                    <b>勤務地までの時間:</b> {duration}<br>
                    """

            popup = folium.Popup(popup_html, max_width=400)
            folium.Marker(
                [row['緯度'], row['経度']],
                popup=popup
            ).add_to(m)
    
    if show_supermarkets and supermarket_df is not None:
        filtered_supermarket_df = supermarket_df[supermarket_df['区'].isin(filtered_df['区'].unique())]
        for idx, row in filtered_supermarket_df.iterrows():
            if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
                popup_html = f"""
                <b>店舗名称:</b> {row['店舗名称']}<br>
                """
                popup = folium.Popup(popup_html, max_width=200)
                folium.Marker(
                    [row['Latitude'], row['Longitude']],
                    popup=popup,
                    icon=folium.Icon(color='green', icon='shopping-cart')
                ).add_to(m)
    
    if show_convenience_stores and convenience_store_df is not None:
        filtered_convenience_store_df = convenience_store_df[convenience_store_df['区'].isin(filtered_df['区'].unique())]
        for idx, row in filtered_convenience_store_df.iterrows():
            if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
                popup_html = f"""
                <b>店舗名称:</b> {row['店舗名称']}<br>
                """
                popup = folium.Popup(popup_html, max_width=200)
                folium.Marker(
                    [row['Latitude'], row['Longitude']],
                    popup=popup,
                    icon=folium.Icon(color='orange', icon='info-sign')
                ).add_to(m)
    
    if show_banks and bank_df is not None:
        filtered_bank_df = bank_df[bank_df['区'].isin(filtered_df['区'].unique())]
        for idx, row in filtered_bank_df.iterrows():
            if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
                popup_html = f"""
                <b>店舗名称:</b> {row['店舗名称']}<br>
                """
                popup = folium.Popup(popup_html, max_width=200)
                folium.Marker(
                    [row['Latitude'], row['Longitude']],
                    popup=popup,
                    icon=folium.Icon(color='red', icon='usd')
                ).add_to(m)
    
    if show_cafes and cafe_df is not None:
        filtered_cafe_df = cafe_df[cafe_df['区'].isin(filtered_df['区'].unique())]
        for idx, row in filtered_cafe_df.iterrows():
            if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
                popup_html = f"""
                <b>店舗名称:</b> {row['店舗名称']}<br>
                """
                popup = folium.Popup(popup_html, max_width=200)
                folium.Marker(
                    [row['Latitude'], row['Longitude']],
                    popup=popup,
                    icon=folium.Icon(color='purple', icon='coffee')
                ).add_to(m)
    
    return m

def display_search_results(filtered_df, workplace_coords):
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    
    for idx, row in filtered_df.iterrows():
        st.write(f"### 物件番号: {idx+1}")
        st.write(f"**名称:** {row['名称']}")
        st.write(f"**アドレス:** {row['アドレス']}")
        st.write(f"**階数:** {row['階数']}")
        st.write(f"**家賃:** {row['家賃']}万円")
        st.write(f"**間取り:** {row['間取り']}")
        st.write(f"**物件詳細URL:** {make_clickable(row['物件詳細URL'], 'リンク')}", unsafe_allow_html=True)
        if pd.notnull(row['物件画像URL']) and pd.notnull(row['間取画像URL']):
            col1, col2 = st.columns(2)
            with col1:
                st.image(row['物件画像URL'], width=300)
            with col2:
                st.image(row['間取画像URL'], width=300)
        elif pd.notnull(row['物件画像URL']):
            st.image(row['物件画像URL'], width=300)
        elif pd.notnull(row['間取画像URL']):
            st.image(row['間取画像URL'], width=300)
        
        if workplace_coords:
            distance, duration = calculate_distance_and_time(gmaps, workplace_coords, (row['緯度'], row['経度']))
            st.write(f"Debug: Workplace Coords: {workplace_coords}, Property Coords: {(row['緯度'], row['経度'])}")
            st.write(f"Debug: Distance: {distance}, Duration: {duration}")
            if distance and duration:
                st.write(f"**勤務地までの距離:** {distance}")
                st.write(f"**勤務地までの時間:** {duration}")
            else:
                st.write("**勤務地までの距離と時間の計算に失敗しました。**")

        if st.button(f"お気に入り登録", key=f"favorite_{idx+1}"):
            save_favorite_property(st.session_state['username'], idx+1)
            st.success(f"{row['名称']}をお気に入りに追加しました")
        st.write("---")

def save_favorite_property(username, property_id):
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_DB_ID).worksheet("お気に入りDB")
    sheet.append_row([username, property_id])

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
    st.title("物件検索")

    if not st.session_state.get('logged_in', False):
        st.warning("ログインしてください")
        st.write("ログインページへ移動")
        return

    df = load_data_from_gsheet(SPREADSHEET_DB_ID, "物件DB")
    df = preprocess_dataframe(df)

    supermarket_df = load_data_from_gsheet(SPREADSHEET_DB_ID, "スーパーDB")
    convenience_store_df = load_data_from_gsheet(SPREADSHEET_DB_ID, "コンビニDB")
    bank_df = load_data_from_gsheet(SPREADSHEET_DB_ID, "銀行DB")
    cafe_df = load_data_from_gsheet(SPREADSHEET_DB_ID, "カフェDB")

    with st.sidebar:
        area = st.radio('■ エリア選択', df['区'].unique())
        price_min, price_max = st.slider(
            '■ 家賃範囲 (万円)',
            min_value=float(1),
            max_value=50.0,
            value=(float(df['家賃'].min()), 50.0),
            step=1.0,
            format='%.1f'
        )
        type_options = st.multiselect('■ 間取り選択', df['間取り'].unique(), default=['1K', '1LDK', '2LDK'])
        workplace_address = st.text_input("■ 現在の勤務地住所を入力")
        workplace_coords = None
        if workplace_address:
            gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
            try:
                geocode_result = gmaps.geocode(workplace_address)
                if geocode_result:
                    workplace_coords = (geocode_result[0]['geometry']['location']['lat'], geocode_result[0]['geometry']['location']['lng'])
            except googlemaps.exceptions.ApiError as e:
                st.error(f"Google Maps API error: {e}")
            except Exception as e:
                st.error(f"Error geocoding address: {e}")

        show_supermarkets = st.checkbox("スーパー", value=False)
        show_convenience_stores = st.checkbox("コンビニ", value=False)
        show_banks = st.checkbox("銀行", value=False)
        show_cafes = st.checkbox("カフェ", value=False)

        if st.button('検索＆更新', key='search_button'):
            st.session_state['filtered_df'] = df[(df['区'].isin([area])) & (df['間取り'].isin(type_options))]
            st.session_state['filtered_df'] = st.session_state['filtered_df'][(st.session_state['filtered_df']['家賃'] >= price_min) & (st.session_state['filtered_df']['家賃'] <= price_max)]
            st.session_state['filtered_df2'] = st.session_state['filtered_df'].dropna(subset=['緯度', '経度'])
            st.session_state['search_clicked'] = True
            st.session_state['selected_property'] = None

    if st.session_state.get('search_clicked', False):
        filtered_count = len(st.session_state['filtered_df'])
        total_count = len(df)
        st.write(f"物件検索数: {filtered_count}件 / 全{total_count}件")

        filtered_df2 = st.session_state.get('filtered_df2', st.session_state['filtered_df'])
        m = create_map(
            filtered_df2,
            workplace_coords,
            show_supermarkets,
            supermarket_df,
            show_convenience_stores,
            convenience_store_df,
            show_banks,
            bank_df,
            show_cafes,
            cafe_df
        )
        folium_static(m)

        selected_property = st.session_state.get('selected_property', None)
        if selected_property is not None:
            display_search_results(selected_property, workplace_coords)
        else:
            display_search_results(st.session_state['filtered_df'], workplace_coords)

if __name__ == '__main__':
    main()
