import streamlit as st

st.set_page_config(
    page_title="Kalender Tanam Singkong",
    layout="wide"
)

# inject CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.switch_page("pages/1_📅_Kalender_Tanam.py")
