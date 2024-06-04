import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import folium
from streamlit_folium import folium_static
from config import SPREADSHEET_DB_ID, scopes

def get_credentials():
    return Credentials.from_service_account_info(st.secrets["PRIVATE_KEY_PATH"], scopes=scopes)

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

def create_map(filtered_df, show_supermarkets, supermarket_df=None, show_convenience_stores=False, convenience_store_df=None, show_banks=False, bank_df=None, show_cafes=False, cafe_df=None):
    map_center = [filtered_df['緯度'].mean(), filtered_df['経度'].mean()]
    m = folium.Map(location=map_center, zoom_start=12)
    for idx, row in filtered_df.iterrows():
        if pd.notnull(row['緯度']) and pd.notnull(row['経度']):
            popup_html = f"""
            <b>名称:</b> {row['名称']}<br>
            <b>アドレス:</b> {row['アドレス']}<br>
            <b>家賃:</b> {row['家賃']}万円<br>
            <b>間取り:</b> {row['間取り']}<br>
            <a href="{row['物件詳細URL']}" target="_blank">物件詳細</a>
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
                    icon=folium.Icon(color='blue', icon='info-sign')
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

def display_search_results(filtered_df):
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
    fav_df = [(fav_df['username'] != username) | (fav_df['property_id'] != property_id)]
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
            max_value=float(df['家賃'].max()),
            value=(float(df['家賃'].min()), float(df['家賃'].max())),
            step=0.1,
            format='%.1f'
        )
        type_options = st.multiselect('■ 間取り選択', df['間取り'].unique(), default=df['間取り'].unique())
        show_supermarkets = st.checkbox("スーパー", value=True)
        show_convenience_stores = st.checkbox("コンビニ", value=True)
        show_banks = st.checkbox("銀行", value=True)
        show_cafes = st.checkbox("カフェ", value=True)
    
    filtered_df = df[(df['区'].isin([area])) & (df['間取り'].isin(type_options))]
    filtered_df = filtered_df[(df['家賃'] >= price_min) & (df['家賃'] <= price_max)]
    filtered_count = len(filtered_df)

    filtered_df['緯度'] = pd.to_numeric(filtered_df['緯度'], errors='coerce')
    filtered_df['経度'] = pd.to_numeric(filtered_df['経度'], errors='coerce')
    filtered_df2 = filtered_df.dropna(subset=['緯度', '経度'])
    filtered_df['物件詳細URL'] = filtered_df['物件詳細URL'].apply(lambda x: make_clickable(x, "リンク"))

    st.write(f"物件検索数: {filtered_count}件 / 全{len(df)}件")
    if st.button('検索＆更新', key='search_button'):
        st.session_state['filtered_df'] = filtered_df
        st.session_state['filtered_df2'] = filtered_df2
        st.session_state['search_clicked'] = True
    
    if st.session_state.get('search_clicked', False):
        m = create_map(st.session_state.get('filtered_df2', filtered_df2), show_supermarkets, supermarket_df, show_convenience_stores, convenience_store_df, show_banks, bank_df, show_cafes, cafe_df)
        folium_static(m)

        # HTML for legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 150px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color:white;
                    ">&nbsp; <b>Legend</b> <br>
                      &nbsp; <i class="fa fa-map-marker fa-2x" style="color:green"></i>&nbsp; スーパー<br>
                      &nbsp; <i class="fa fa-map-marker fa-2x" style="color:blue"></i>&nbsp; コンビニ<br>
                      &nbsp; <i class="fa fa-map-marker fa-2x" style="color:red"></i>&nbsp; 銀行<br>
                      &nbsp; <i class="fa fa-map-marker fa-2x" style="color:purple"></i>&nbsp; カフェ
        </div>
        '''

        # Display legend in map
        m.get_root().html.add_child(folium.Element(legend_html))

        show_all_option = st.radio(
            "表示オプションを選択してください:",
            ('地図上の検索物件のみ', 'すべての検索物件'),
            index=0 if not st.session_state.get('show_all', False) else 1,
            key='show_all_option'
        )
        st.session_state['show_all'] = (show_all_option == 'すべての検索物件')
        if st.session_state['show_all']:
            display_search_results(st.session_state.get('filtered_df', filtered_df))
        else:
            display_search_results(st.session_state.get('filtered_df2', filtered_df2))

if __name__ == '__main__':
    main()
