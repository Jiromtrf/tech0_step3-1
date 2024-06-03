import streamlit as st

def main():
    st.write("SPREADSHEET_DB_ID:", st.secrets["SPREADSHEET_DB_ID"])
    st.write("LINE_NOTIFY_TOKEN:", st.secrets["LINE_NOTIFY_TOKEN"])
    st.write("PRIVATE_KEY:", st.secrets["PRIVATE_KEY"])

if __name__ == "__main__":
    main()
